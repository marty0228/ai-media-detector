import os
import sys
import torch
from PIL import Image
from io import BytesIO
import numpy as np

# 현재 위치의 trufor 디렉토리를 파이썬 시스템 패스에 추가 (내부 config, 모델 등을 쉽게 import하기 위함)
trufor_path = os.path.join(os.path.dirname(__file__), 'trufor')
if trufor_path not in sys.path:
    sys.path.insert(0, trufor_path)

try:
    from config import _C as config
    from models.cmx.builder_np_conf import myEncoderDecoder as confcmx
except ImportError as e:
    print(f"Warning: Failed to import TruFor modules: {e}")

# 메모리에 한번만 올리기 위한 전역 캐시
_model = None
_device = None

def load_model():
    """서버 기동 시 TruFor 모델의 아키텍처와 가중치를 메모리에 올립니다."""
    global _model, _device
    print("Loading Forensic Analysis (TruFor) Model...")
    
    _device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 가중치 파일 경로 확인
    weights_dir = os.path.join(trufor_path, 'weights')
    weights_path = os.path.join(weights_dir, 'trufor.pth.tar')
    
    if not os.path.exists(weights_path):
        print(f"-> WARNING: TruFor weight file not found at {weights_path}.")
        print("-> Please download 'trufor.pth.tar' and place it in the weights/ directory.")
        return

    # 모델 구조체 초기화 및 가중치 삽입
    try:
        _model = confcmx(cfg=config)
        checkpoint = torch.load(weights_path, map_location=_device, weights_only=False)
        _model.load_state_dict(checkpoint['state_dict'])
        _model = _model.to(_device)
        _model.eval()
        print("-> TruFor weights loaded successfully!")
    except Exception as e:
        print(f"-> Error initializing TruFor model: {e}")
        _model = None


def predict(image_bytes: bytes) -> dict:
    """Bytes 이미지를 TruFor 모델에 통과시켜 조작 확률(confidence)을 산출하여 반환합니다."""
    global _model, _device
    
    if _model is None:
        load_model()
        
    try:
        if _model is None:
            # 가중치(웨이트)가 없어서 모델 초기화가 안 되었다면 기본(평균적인 중립) 결과 스킵 처리
            return {
                "model_name": "Model 5",
                "predicted_idx": 1,
                "confidence": 0.5,
                "error": "trufor.pth.tar weight file is missing."
            }
            
        # 입력된 바이트 이미지를 RGB 형태로 변환
        image = Image.open(BytesIO(image_bytes)).convert('RGB')
        img_np = np.array(image)
        
        # TruFor의 myDataset과 동일한 스케일링/텐서화 규칙: (H, W, C) -> (C, H, W) 후 256.0으로 나눔
        img_tensor = torch.tensor(img_np.transpose(2, 0, 1), dtype=torch.float) / 256.0
        
        # 모델의 입력을 위해 맨 앞에 Batch Dimension 추가: (1, C, H, W)
        img_tensor = img_tensor.unsqueeze(0).to(_device)
        
        # 모델 추론 진행 (No grad 속도개선)
        with torch.no_grad():
            # 반환값: pred(segmentation map), conf(의심구역 컨피던스맵), det(전체 탐지 점수), npp(노이즈프린트)
            pred, conf, det, npp = _model(img_tensor)
            
            # det 값에서 이미지 전체 레벨 조작 판별 확률 (sigmoid)
            if det is not None:
                det_prob = torch.sigmoid(det).item()
            else:
                det_prob = 0.5

            predicted_idx = 1 if det_prob >= 0.5 else 0
            
            return {
                "model_name": "Model 5",
                "predicted_idx": predicted_idx,
                "confidence": round(det_prob, 4),
            }
            
    except Exception as e:
        print(f"Forensic Analysis prediction error: {e}")
        return {
            "model_name": "Model 5",
            "predicted_idx": 0,
            "confidence": 0.5,
            "error": str(e)
        }
