import io
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# 1. 모델과 가중치를 전역 변수로 관리 (서버 시작 시 한 번만 로드)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = None

# 2. 이미지 전처리 로직 (ResNet이 기대하는 기본 스펙)
image_transforms = transforms.Compose([
    transforms.Resize(256),             # 짧은 쪽을 256으로 리사이즈
    transforms.CenterCrop(224),         # 중앙 224x224 크루프
    transforms.ToTensor(),              # PyTorch Tensor로 변환
    transforms.Normalize(               # ImageNet 정규화 수치
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def load_ai_model():
    """
    ResNet-50 구조를 준비하고, 마지막 분류(FC) 레이어를 2개의 클래스 출력으로 수정합니다.
    """
    global model
    print(f"Loading ResNet-50 (2-class architecture)... Device: {device}")
    
    # 기본 ResNet-50 가져오기 (가중치 없이 구조만. 추후 학습 가중치를 덮어씌울 예정)
    model = models.resnet50()
    
    # 기존 모델의 마지막 출력이 1000개인데, 이를 2개(0: Real, 1: Fake)로 변경
    num_ftrs = model.fc.in_features
    # nn.Linear(in_features, out_features)
    model.fc = nn.Linear(num_ftrs, 2)
    
    # TODO: 추후 이곳에 `model.load_state_dict(torch.load('my_trained_weights.pth'))` 추가 예정
    
    model = model.to(device)
    model.eval()  # 추론 모드 설정
    print("ResNet-50 architecture initialized successfully.")

def predict_image(image_bytes: bytes) -> dict:
    """
    클라이언트에서 받은 이미지 바이트를 전처리하고, 모델에 통과시켜 결과를 반환합니다.
    """
    global model
    if model is None:
        raise RuntimeError("AI Model is not loaded.")
        
    try:
        # 바이트 데이터를 PIL 이미지로 엽니다.
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # 정의해둔 전처리 적용
        tensor = image_transforms(image).unsqueeze(0) # 배치 차원 추가 [1, C, H, W]
        tensor = tensor.to(device)
        
        # 모델 추론 진행 
        # (학습이 안 되어있으므로, 지금은 무작위 값에 가까운 결과가 나옵니다.)
        with torch.no_grad():
            outputs = model(tensor)
            
        # 소프트맥스로 확률(%) 계산
        probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
        
        # 가장 높은 확률을 가진 클래스의 인덱스 (0: 진짜, 1: AI 생성)
        confidence, predicted_idx = torch.max(probabilities, 0)
        
        # 파이썬 기본 데이터 타입으로 변환
        predicted_idx = predicted_idx.item()
        confidence = confidence.item()
        
        return {
            "prediction": "AI Generated" if predicted_idx == 1 else "Real",
            "predicted_idx": predicted_idx,  # 0 or 1
            "confidence": f"{confidence * 100:.2f}%"
        }
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        return {
            "error": str(e)
        }
