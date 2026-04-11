import os, joblib
import pandas as pd
import mlflow
import mlflow.sklearn

MLFLOW_TRACKING_URI = "https://mlflow-server-7852824563.asia-northeast3.run.app"

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
    
    if os.path.exists(c_path):
        trained_columns = joblib.load(c_path)
        
    try:
        # 클라우드 런 MLflow에서 최신 모델 불러오기 시도
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment("AI_Media_Detector_MetaData")
        experiment = mlflow.get_experiment_by_name("AI_Media_Detector_MetaData")
        if experiment:
            client = mlflow.tracking.MlflowClient()
            runs = client.search_runs(experiment_ids=[experiment.experiment_id], order_by=["start_time DESC"], max_results=1)
            if runs:
                latest_run_id = runs[0].info.run_id
                model = mlflow.sklearn.load_model(f"runs:/{latest_run_id}/rf_model")
                print("Meta Data AI model loaded successfully from MLflow (Cloud Run).")
                return
    except Exception as e:
        print(f"Warning: Failed to load model from MLflow Cloud Run ({e}). Falling back to local pickle.")

    if os.path.exists(m_path) and os.path.exists(c_path):
        model, trained_columns = joblib.load(m_path), joblib.load(c_path)
        print("Meta Data AI model loaded successfully from local pickle.")
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