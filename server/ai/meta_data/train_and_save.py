import os
import joblib
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

MLFLOW_TRACKING_URI = "https://mlflow-server-7852824563.asia-northeast3.run.app"
MLFLOW_EXPERIMENT_NAME = "AI_Media_Detector_MetaData"
MLFLOW_COLUMNS_ARTIFACT_DIR = "metadata_artifacts"

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

print("Starting meta data model training...")
base_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(base_dir, "model", "metadata_dataset_expanded.csv")).dropna(subset=["label"])
df = df.fillna(
    {
        "make_raw": "None",
        "model_raw": "None",
        "camera_brand": "none",
        "software_raw": "None",
        "software_type": "none",
    }
)
df["label"] = df["label"].astype(int)

X = df.drop(columns=["label", "filename", "make_raw", "model_raw", "software_raw"], errors="ignore")
y = df["label"]

cat_cols = [c for c in ["camera_brand", "software_type"] if c in X.columns]
if cat_cols:
    X = pd.get_dummies(X, columns=cat_cols)
X = X.astype({c: int for c in X.columns if X[c].dtype == "bool"})

X_train, X_valid, y_train, y_valid = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

with mlflow.start_run():
    n_estimators = 300
    max_depth = 10
    min_samples_split = 4
    min_samples_leaf = 2

    mlflow.log_params(
        {
            "model_type": "RandomForest",
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "min_samples_split": min_samples_split,
            "min_samples_leaf": min_samples_leaf,
            "random_state": 42,
            "class_weight": "balanced",
        }
    )

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_valid)
    acc = accuracy_score(y_valid, y_pred)
    mlflow.log_metric("accuracy", acc)

    print(
        f"\nValidation Accuracy: {acc:.4f}\n\n"
        f"Confusion Matrix:\n{confusion_matrix(y_valid, y_pred)}\n\n"
        f"Classification Report:\n{classification_report(y_valid, y_pred, digits=4)}"
    )

    feat_df = pd.DataFrame(
        {"feature": X_train.columns, "importance": model.feature_importances_}
    ).sort_values(by="importance", ascending=False)
    feat_csv = os.path.join(base_dir, "model", "feature_importance.csv")
    feat_df.to_csv(feat_csv, index=False, encoding="utf-8-sig")

    model_path = os.path.join(base_dir, "model", "rf_metadata_model.pkl")
    cols_path = os.path.join(base_dir, "model", "model_columns.pkl")
    joblib.dump(model, model_path)
    joblib.dump(X_train.columns.tolist(), cols_path)

    mlflow.sklearn.log_model(model, "rf_model")
    mlflow.log_artifact(cols_path, artifact_path=MLFLOW_COLUMNS_ARTIFACT_DIR)
    mlflow.log_artifact(feat_csv, artifact_path=MLFLOW_COLUMNS_ARTIFACT_DIR)

    print(
        f"\nTraining complete\n"
        f"- model: {model_path}\n"
        f"- columns: {cols_path}\n"
        f"- importance: {feat_csv}"
    )
