import os
import io
import sys
import tempfile
from pathlib import Path

from PIL import Image

try:
    from huggingface_hub import snapshot_download
except ImportError:
    snapshot_download = None


ai_detector = None


# ---------------------------------------------------------
# 1. 모델 초기화 및 로드
# ---------------------------------------------------------
def load_model():
    global ai_detector

    print("Loading Visual anomaly AI model...")

    try:
        repo_id = "Bombek1/ai-image-detector-siglip-dinov2"
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        local_model_dir = os.path.join(
            base_path,
            "models",
            "ai_detector_siglip_dinov2"
        )

        # Hugging Face에서 모델 파일 다운로드
        # 이미 다운로드되어 있으면 로컬 파일을 재사용함
        model_dir = snapshot_download(
            repo_id=repo_id,
            local_dir=local_model_dir
        )

        # Hugging Face repo 안의 model.py import를 위해 경로 추가
        if model_dir not in sys.path:
            sys.path.insert(0, model_dir)

        try:
            from model import AIImageDetector
        except ImportError as e:
            print(f"Warning: Failed to import AIImageDetector from model.py: {e}")
            ai_detector = None
            return

        weights_path = os.path.join(model_dir, "pytorch_model.pt")

        if not os.path.exists(weights_path):
            print(f"Warning: AI detector weights not found at {weights_path}")
            ai_detector = None
            return

        ai_detector = AIImageDetector(weights_path)

        print("AI Image Detector model loaded successfully.")

    except Exception as e:
        print(f"Error while loading AI Image Detector model: {e}")
        ai_detector = None


# ---------------------------------------------------------
# 2. 이미지 바이트 기반 AI 생성물 예측 실행
# ---------------------------------------------------------
def predict(image_bytes: bytes) -> dict:
    global ai_detector

    # 모델 로드 실패 시 더미 데이터 반환
    if ai_detector is None:
        return {
            "model_name": "AI Image Detector",
            "predicted_idx": 0,
            "confidence": 0.0
        }

    try:
        # 바이트 배열을 PIL 이미지로 변환
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # 모델 추론 수행
        result = ai_detector.predict(image)

        # result 예시:
        # {
        #     "prediction": "AI-generated",
        #     "confidence": 0.97,
        #     "probability": 0.97
        # }

        p_ai = float(result.get("probability", 0.0))
        confidence = float(result.get("confidence", p_ai))

        # threshold는 필요에 따라 조정 가능
        # 0.5는 기본 분류 기준, 실사용에서는 0.7~0.85 추천
        predicted_idx = 1 if p_ai >= 0.5 else 0
        print(p_ai, confidence)
        return {
            "model_name": "Visual anomaly",
            "predicted_idx": predicted_idx,
            "confidence": p_ai
        }

    except Exception as e:
        print(f"Error in Visual anomaly prediction: {e}")

        return {
            "model_name": "Visual anomaly",
            "predicted_idx": 0,
            "confidence": 0.0
        }


if __name__ == "__main__":
    load_model()