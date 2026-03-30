import os
import pandas as pd
import joblib
try:
    from ai.meta_data.fetch_metadata import extract_metadata
except ModuleNotFoundError:
    from fetch_metadata import extract_metadata

model = None
trained_columns = None

def load_model():
    global model, trained_columns

    print("Loading Meta Data AI model...")
    base_path = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_path, 'rf_metadata_model.pkl')
    columns_path = os.path.join(base_path, 'model_columns.pkl')
    
    if os.path.exists(model_path) and os.path.exists(columns_path):
        model = joblib.load(model_path)
        trained_columns = joblib.load(columns_path)
        print("Meta Data AI model loaded successfully.")
    else:
        print("Warning: Meta Data model files not found. Creating a dummy model output.")

def predict(image_bytes: bytes) -> dict:
    #바이트 형식의 이미지를 받아 메타데이터 기반으로 AI 생성물인지 판별합니다.
    
    global model, trained_columns
    
    if model is None or trained_columns is None:
        print("Meta Data model not loaded or missing. Returning dummy prediction.")
        return {
            "model_name": "Meta Data",
            "predicted_idx": 0,
            "confidence": 0.0
        }

    # 메타데이터 추출
    metadata = extract_metadata(image_bytes, label=-1)
    
    # DataFrame 변환
    df_test = pd.DataFrame([metadata])
    
    # 전처리
    X_test = df_test.drop(columns=['label', 'filename'], errors='ignore')
    X_test = pd.get_dummies(X_test, columns=['software'])
    
    # 학습 시 저장해둔 컬럼(trained_columns)과 맞추기
    X_test = X_test.reindex(columns=trained_columns, fill_value=0)
    
    # 확률 예측
    probabilities = model.predict_proba(X_test)
    ai_prob = probabilities[0, 1]  # AI일 확률
    
    return {
        "model_name": "Meta Data",
        "predicted_idx": 1 if ai_prob >= 0.5 else 0,
        "confidence": float(ai_prob)
    }

if __name__ == "__main__":
    load_model()