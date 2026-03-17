import io
import torch
from PIL import Image
from transformers import pipeline

# 1. Hugging Face 파이프라인 전역 변수로 관리 (서버 시작 시 한 번만 로드)
pipe = None

def load_ai_model():
    """
    Hugging Face에서 사전 학습된 뛰어난 AI 이미지 판별 모델(ViT 기반)을 불러옵니다.
    처음 실행 시에는 약 300MB 이상의 모델 가중치를 자동으로 다운로드합니다.
    """
    global pipe
    print("Loading Pre-trained AI Detection Model (umm-maybe/AI-image-detector)...")
    
    # 'image-classification' 파이프라인으로 이미 학습된 모델을 지정
    # 이 모델은 이미지에 대해 "artificial"(AI 생성) 또는 "human"(진짜) 등의 라벨과 확률을 반환합니다.
    pipe = pipeline("image-classification", model="umm-maybe/AI-image-detector")
    
    print("AI Detection Model loaded successfully.")

def predict_image(image_bytes: bytes) -> dict:
    """
    클라이언트에서 받은 이미지 바이트를 PIL 이미지로 열고, 모델에 통과시켜 결과를 반환합니다.
    """
    global pipe
    if pipe is None:
        raise RuntimeError("AI Model is not loaded.")
        
    try:
        # 바이트 데이터를 PIL 이미지로 엽니다. (RGB 모드로 변환)
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # 파이프라인을 통해 예측 수행
        # 파이프라인의 결과는 리스트 안의 딕셔너리 형태입니다.
        # 예: [{'label': 'artificial', 'score': 0.98}, {'label': 'human', 'score': 0.02}]
        results = pipe(image)
        
        # 가장 점수(score)가 높은 첫 번째 결과를 가져옵니다.
        top_prediction = results[0]
        label = top_prediction['label']
        score = top_prediction['score']
        
        # 라벨에 따라 결과를 매핑합니다.
        # 결과값에 따라 인덱스 지정: 가짜(artificial/AI) = 1, 진짜(human/real) = 0
        predicted_idx = 1 if label == 'artificial' else 0
        prediction_text = "AI Generated" if predicted_idx == 1 else "Real"
        
        return {
            "prediction": prediction_text,
            "predicted_idx": predicted_idx,  # 0 or 1
            "confidence": f"{score * 100:.2f}%"
        }
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        return {
            "error": str(e)
        }
