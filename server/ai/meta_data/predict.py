import os
import joblib
import pandas as pd
import mlflow
import mlflow.sklearn

MLFLOW_TRACKING_URI = "https://mlflow-server-7852824563.asia-northeast3.run.app"
MLFLOW_EXPERIMENT_NAME = "AI_Media_Detector_MetaData"
MLFLOW_COLUMNS_ARTIFACT_PATH = "metadata_artifacts/model_columns.pkl"
USE_MLFLOW = os.getenv("USE_MLFLOW", "true").strip().lower() in {"1", "true", "yes", "on"}

try:
    from ai.meta_data.fetch_metadata import extract_metadata
except ModuleNotFoundError:
    from fetch_metadata import extract_metadata

model, trained_columns = None, None


def _load_local_model(model_path: str, columns_path: str) -> bool:
    global model, trained_columns

    if not (os.path.exists(model_path) and os.path.exists(columns_path)):
        print("Warning: Meta Data model files not found locally.")
        return False

    model = joblib.load(model_path)
    trained_columns = joblib.load(columns_path)
    print("Meta Data AI model loaded successfully from local pickle.")
    return True


def _load_mlflow_model() -> bool:
    global model, trained_columns

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    experiment = mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME)
    if not experiment:
        print(f"Warning: MLflow experiment '{MLFLOW_EXPERIMENT_NAME}' not found.")
        return False

    client = mlflow.tracking.MlflowClient()
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"],
        max_results=1,
    )
    if not runs:
        print("Warning: No MLflow runs found for Meta Data model.")
        return False

    latest_run_id = runs[0].info.run_id
    model = mlflow.sklearn.load_model(f"runs:/{latest_run_id}/rf_model")
    columns_path = mlflow.artifacts.download_artifacts(
        artifact_uri=f"runs:/{latest_run_id}/{MLFLOW_COLUMNS_ARTIFACT_PATH}"
    )
    trained_columns = joblib.load(columns_path)
    print(f"Meta Data AI model loaded successfully from MLflow run {latest_run_id}.")
    return True


def load_model():
    global model, trained_columns

    print("Loading Meta Data AI model...")
    base_path = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_path, "model", "rf_metadata_model.pkl")
    columns_path = os.path.join(base_path, "model", "model_columns.pkl")

    if USE_MLFLOW:
        try:
            # Keep the model and feature columns in sync by loading both from one run.
            if _load_mlflow_model():
                return
        except Exception as e:
            print(f"Warning: Failed to load model from MLflow Cloud Run ({e}). Falling back to local pickle.")

    _load_local_model(model_path, columns_path)


def predict(image_bytes: bytes) -> dict:
    global model, trained_columns

    if model is None or trained_columns is None:
        return {"model_name": "Meta Data", "predicted_idx": 0, "confidence": 0.0}

    df = pd.DataFrame([extract_metadata(image_bytes)])
    X = df.drop(columns=["label", "filename", "make_raw", "model_raw", "software_raw"], errors="ignore")

    cat_cols = [c for c in ["camera_brand", "software_type"] if c in X.columns]
    if cat_cols:
        X = pd.get_dummies(X, columns=cat_cols)
    X = X.reindex(columns=trained_columns, fill_value=0)

    ai_prob = float(model.predict_proba(X)[0, 1])
    return {"model_name": "Meta Data", "predicted_idx": int(ai_prob >= 0.5), "confidence": ai_prob}


if __name__ == "__main__":
    load_model()
