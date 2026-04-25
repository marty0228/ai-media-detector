import os
import torch
from io import BytesIO
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
import mlflow
import mlflow.pytorch

# model.py 와 같은 모듈 공간에서 불러옴
try:
    from ai.visual_anomaly.model import VisualAnomalyResNet
except ModuleNotFoundError:
    from model import VisualAnomalyResNet

MLFLOW_TRACKING_URI = "https://mlflow-server-7852824563.asia-northeast3.run.app"

# 글로벌 변수로 모델 캐싱
_model = None
_device = None
_transforms = None

def load_model():
    """
    서버 시작 시 호출되어 PyTorch 시각적 이상 평가 모델 세팅
    """
    global _model, _device, _transforms
    
    print("Loading visual_anomaly model (ResNet50)...")
    
    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # ImageNet 정규화 표준
    _transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    try:
        # 클라우드 런 MLflow에서 최신 모델 불러오기 시도
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment("AI_Media_Detector_Visual_Anomaly")
        experiment = mlflow.get_experiment_by_name("AI_Media_Detector_Visual_Anomaly")
        if experiment:
            client = mlflow.tracking.MlflowClient()
            runs = client.search_runs(experiment_ids=[experiment.experiment_id], order_by=["start_time DESC"], max_results=1)
            if runs:
                latest_run_id = runs[0].info.run_id
                _model = mlflow.pytorch.load_model(f"runs:/{latest_run_id}/resnet_model")
                _model = _model.to(_device)
                _model.eval()
                print("visual_anomaly model loaded successfully from MLflow (Cloud Run).")
                return
    except Exception as e:
        print(f"Warning: Failed to load model from MLflow Cloud Run ({e}). Falling back to local weight.")

    # 모델 아키텍처 불러오기
    _model = VisualAnomalyResNet(pretrained=False) # 추론 시엔 Imagenet weight 다운로드 불필요
    
    weight_path = os.path.join(os.path.dirname(__file__), "visual_anomaly.pth")
    if os.path.exists(weight_path):
        _model.load_state_dict(torch.load(weight_path, map_location=_device))
        print("-> PyTorch weights loaded successfully from local.")
    else:
        print(f"-> WARNING: Weight file not found at {weight_path}. Model will output random values.")
        
    _model = _model.to(_device)
    _model.eval()


def predict(image_bytes: bytes) -> dict:
    """
    Transfer Learning 된 모델로부터 AI 생성 확률을 반환합니다.
    """
    global _model, _device, _transforms
    
    if _model is None:
        load_model()
        
    try:
        # Pytorch PIL 변환
        image = Image.open(BytesIO(image_bytes)).convert('RGB')
        input_tensor = _transforms(image).unsqueeze(0).to(_device)
        
        with torch.no_grad():
            outputs = _model(input_tensor)
            
            # 여기서 클래스 예측. (보통 클래스 0: AI, 클래스 1: REAL 혹은 역순일 수 있음)
            # 여기서는 [REAL, AI] 순서의 폴더명(알파벳순)을 가정합니다. a, r -> ai: 0, real: 1
            # 만약 Train할 때 DataFolder 기본값을 쓰면 'ai'가 0번 인덱스, 'real'이 1번 인덱스가 됩니다.
            # 우리가 원하는 confidence는 AI 확률이므로 AI 인덱스의 Softmax 값을 취합니다.
            probabilities = F.softmax(outputs, dim=1)
            
            # 폴더명 순서에 맞춰 ai가 0, real이 1인 경우
            # AI일 확률:
            ai_prob = probabilities[0][0].item() # 0번 인덱스가 'ai'라 가정
            
            predicted_idx = 1 if ai_prob >= 0.5 else 0
            
            return {
                "model_name": "visual_anomaly",
                "predicted_idx": predicted_idx,
                "confidence": round(ai_prob, 4)
            }
            
    except Exception as e:
        print(f"Visual Anomaly prediction error: {e}")
        return {
            "model_name": "visual_anomaly",
            "predicted_idx": 0,
            "confidence": 0.5,
            "error": str(e)
        }
