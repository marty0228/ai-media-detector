import os, joblib
import pandas as pd

try:
    from ai.meta_data.fetch_metadata import extract_metadata
except ModuleNotFoundError:
    from fetch_metadata import extract_metadata

model, trained_columns = None, None

# ---------------------------------------------------------
# 1. 추론을 위한 피클(Pickle) 모델 및 컬럼 구조 파일 로더
# ---------------------------------------------------------
def load_model():
    # 서버 실행 시 미리 학습된 모델과 컬럼 구조 정보를 메모리에 전역 로드
    global model, trained_columns
    print("Loading Meta Data AI model...")
    base_path = os.path.dirname(os.path.abspath(__file__))
    m_path, c_path = os.path.join(base_path, 'model', 'rf_metadata_model.pkl'), os.path.join(base_path, 'model', 'model_columns.pkl')
    
    if os.path.exists(m_path) and os.path.exists(c_path):
        model, trained_columns = joblib.load(m_path), joblib.load(c_path)
        print("Meta Data AI model loaded successfully.")
    else:
        print("Warning: Meta Data model files not found.")

# ---------------------------------------------------------
# 2. 클라이언트 요청(이미지 바이트) 기반 실시간 AI 추론 평가
# ---------------------------------------------------------
def predict(image_bytes: bytes) -> dict:
    global model, trained_columns
    
    # 모델 파일이 누락되었을 경우를 대비한 방어 로직 (기본값 반환)
    if not model or not trained_columns:
        return {"model_name": "Meta Data", "predicted_idx": 0, "confidence": 0.0}

    # 입력 이미지의 메타데이터 추출 및 판별용 데이터프레임 구조화
    df = pd.DataFrame([extract_metadata(image_bytes)])
    X = df.drop(columns=['label', 'filename', 'make_raw', 'model_raw', 'software_raw'], errors='ignore')
    
    cat_cols = [c for c in ['camera_brand', 'software_type'] if c in X.columns]
    if cat_cols: X = pd.get_dummies(X, columns=cat_cols)
    
    # 훈련 시점과 완전히 동일한 컬럼(Feature) 배열로 동기화 처리 (결측값은 0 대체)
    X = X.reindex(columns=trained_columns, fill_value=0)
    
    # 랜덤 포레스트를 통한 최종 확률 검증 도출 및 포맷팅 (0: 오리지널, 1: AI 이미지)
    ai_prob = float(model.predict_proba(X)[0, 1])
    return {"model_name": "Meta Data", "predicted_idx": int(ai_prob >= 0.5), "confidence": ai_prob}

if __name__ == "__main__":
    load_model()