import os
import io
from PIL import Image

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

model = None

# ---------------------------------------------------------
# 1. 모델 초기화 및 로드
# ---------------------------------------------------------
def load_model():
    global model
    print("Loading Watermark AI model (Model 2)...")
    base_path = os.path.dirname(os.path.abspath(__file__))
    weights_path = os.path.join(base_path, 'runs', 'detect', 'watermark_model', 'final_v1', 'weights', 'best.pt')
    
    if YOLO and os.path.exists(weights_path):
        # 저장된 YOLO 모델(Watermark 판별용) 가중치 로드
        model = YOLO(weights_path)
        print("Watermark model (Model 2) loaded successfully.")
    else:
        print(f"Warning: Watermark model files not found at {weights_path} or ultralytics not installed.")

# ---------------------------------------------------------
# 2. 이미지 바이트 기반 워터마크 예측 실행
# ---------------------------------------------------------
def predict(image_bytes: bytes) -> dict:
    global model
    
    # 모델 로드 실패 시 더미 데이터 반환
    if not model:
        return {
            "model_name": "Water Mark",
            "predicted_idx": 0,
            "confidence": 0.0
        }
    
    try:
        # 바이트 배열을 PIL 이미지로 변환
        image = Image.open(io.BytesIO(image_bytes))
        
        # YOLO 예측 수행 (conf=0.01 : 1% 이상 확신할 때 1차 탐지)
        results = model(image, conf=0.01, verbose=False)
        
        max_conf = 0.0
        # 배치(batch) 중 첫 번째 결과 처리
        for r in results:
            if len(r.boxes) > 0:
                # 탐지된 바운딩 박스들 중 가장 높은 신뢰도(Confidence) 점수를 추출
                max_conf = float(r.boxes.conf.max())
                
        return {
            "model_name": "Water Mark",
            "predicted_idx": 1 if max_conf >= 0.5 else 0,
            "confidence": max_conf
        }
        
    except Exception as e:
        print(f"Error in watermark prediction: {e}")
        return {
            "model_name": "Model 2",
            "predicted_idx": 0,
            "confidence": 0.0
        }

if __name__ == "__main__":
    load_model()
