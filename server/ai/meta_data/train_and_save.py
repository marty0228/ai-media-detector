import os
import joblib
import pandas as pd
import mlflow
import mlflow.sklearn
import matplotlib.pyplot as plt

from contextlib import nullcontext

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)

from fetch_metadata import collect_images_from_folder


# ============================================================
# 0. MLflow 설정
# ============================================================

USE_MLFLOW = False

MLFLOW_TRACKING_URI = "https://mlflow-server-7852824563.asia-northeast3.run.app"
MLFLOW_EXPERIMENT_NAME = "AI_Media_Detector_MetaData"
MLFLOW_COLUMNS_ARTIFACT_DIR = "metadata_artifacts"

print("Starting meta data model training...")

if USE_MLFLOW:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)


# ============================================================
# 1. 데이터 로드
# ============================================================

base_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(base_dir, "model")
data_path = os.path.join(model_dir, "metadata_dataset_expanded.csv")

df = pd.read_csv(data_path).dropna(subset=["label"])

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


# ============================================================
# 2. Feature / Label 분리
# ============================================================

X = df.drop(
    columns=["label", "filename", "make_raw", "model_raw", "software_raw"],
    errors="ignore",
)

y = df["label"]

cat_cols = [c for c in ["camera_brand", "software_type"] if c in X.columns]

if cat_cols:
    X = pd.get_dummies(X, columns=cat_cols)

X = X.astype({c: int for c in X.columns if X[c].dtype == "bool"})


# ============================================================
# 3. 추가 feature 확인
# ============================================================
# 이 모델은 추가 feature 3개가 포함된 버전만 사용한다.
# 제거하지 않고 전체 feature를 그대로 사용한다.
# 추가 feature:
# - exif_field_count
# - metadata_key_count
# - is_screenshot_like
# ============================================================

added_features = [
    "exif_field_count",
    "metadata_key_count",
    "is_screenshot_like",
]

existing_added_features = [c for c in added_features if c in X.columns]
missing_added_features = [c for c in added_features if c not in X.columns]

if missing_added_features:
    print("\nWarning: These added features are not found in dataset:")
    print(missing_added_features)
    print("현재 CSV에 해당 컬럼이 없으면 해당 feature 없이 학습됩니다.\n")

print("\nAdded features found in dataset:")
print(existing_added_features)

# 최종 모델은 추가 feature가 포함된 전체 feature 사용
final_columns = X.columns.tolist()
X_final = X[final_columns]

print(f"\nFinal feature count: {len(final_columns)}")


# ============================================================
# 4. Train / Valid Split
# ============================================================

train_idx, valid_idx = train_test_split(
    X.index,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

X_train = X_final.loc[train_idx]
X_valid = X_final.loc[valid_idx]

y_train = y.loc[train_idx]
y_valid = y.loc[valid_idx]

print(f"\nTrain size: {len(y_train)}")
print(f"Valid size: {len(y_valid)}")


# ============================================================
# 5. 공통 학습 설정
# ============================================================

n_estimators = 300
max_depth = 10
min_samples_split = 4
min_samples_leaf = 2


def save_confusion_matrix_image(y_true, y_pred, title, save_path):
    cm = confusion_matrix(y_true, y_pred)

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["Real", "AI"],
    )

    disp.plot(values_format="d")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

    return save_path


def train_and_evaluate(X_train, X_valid, y_train, y_valid, model_name):
    print("\n" + "=" * 70)
    print(model_name)
    print("=" * 70)

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
    precision = precision_score(y_valid, y_pred, zero_division=0)
    recall = recall_score(y_valid, y_pred, zero_division=0)
    f1 = f1_score(y_valid, y_pred, zero_division=0)

    cm = confusion_matrix(y_valid, y_pred)
    report = classification_report(
        y_valid,
        y_pred,
        digits=4,
        zero_division=0,
        target_names=["Real", "AI"],
    )

    safe_model_name = model_name.lower().replace(" ", "_").replace("/", "_")
    cm_image_path = os.path.join(
        model_dir,
        f"{safe_model_name}_confusion_matrix.png",
    )

    save_confusion_matrix_image(
        y_valid,
        y_pred,
        model_name,
        cm_image_path,
    )

    print(f"Validation Accuracy : {acc:.4f}")
    print(f"Precision           : {precision:.4f}")
    print(f"Recall              : {recall:.4f}")
    print(f"F1-score            : {f1:.4f}")
    print(f"\nConfusion Matrix:\n{cm}")
    print(f"\nClassification Report:\n{report}")
    print(f"\nConfusion matrix image saved: {cm_image_path}")

    return {
        "model": model,
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": cm,
        "classification_report": report,
        "confusion_matrix_image": cm_image_path,
    }


# ============================================================
# 6. train_datasets/test 폴더 평가용 함수
# ============================================================

def prepare_manual_test_X(rows, columns):
    df_test = pd.DataFrame(rows)

    X_test = df_test.drop(
        columns=["label", "filename", "make_raw", "model_raw", "software_raw"],
        errors="ignore",
    )

    cat_cols = [c for c in ["camera_brand", "software_type"] if c in X_test.columns]

    if cat_cols:
        X_test = pd.get_dummies(X_test, columns=cat_cols)

    X_test = X_test.astype({c: int for c in X_test.columns if X_test[c].dtype == "bool"})

    # 학습 때 있었는데 테스트 데이터에는 없는 컬럼은 0으로 채움
    for col in columns:
        if col not in X_test.columns:
            X_test[col] = 0

    # 학습 때 없었던 컬럼은 제거하고, 컬럼 순서 맞춤
    X_test = X_test[columns]

    y_test = df_test["label"].astype(int)
    filenames = df_test["filename"]

    return X_test, y_test, filenames


def evaluate_manual_test_folder(model, columns, test_name):
    test_dir = os.path.join(base_dir, "train_datasets", "test")
    real_dir = os.path.join(test_dir, "real")
    ai_dir = os.path.join(test_dir, "ai")

    rows = (
        collect_images_from_folder(real_dir, 0)
        + collect_images_from_folder(ai_dir, 1)
    )

    if not rows:
        print("\nManual test skipped.")
        print("train_datasets/test/real 또는 train_datasets/test/ai 폴더에 이미지가 없습니다.")
        return None

    X_test, y_test, filenames = prepare_manual_test_X(rows, columns)

    y_pred = model.predict(X_test)

    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test)[:, 1]
    else:
        y_prob = [None] * len(y_pred)

    acc = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    report = classification_report(
        y_test,
        y_pred,
        target_names=["Real", "AI"],
        digits=4,
        zero_division=0,
    )

    print("\n" + "=" * 70)
    print(f"Manual Test Folder Result: {test_name}")
    print("=" * 70)
    print(f"Test Images: {len(rows)}")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-score : {f1:.4f}")
    print(f"\nConfusion Matrix:\n{cm}")
    print(f"\nClassification Report:\n{report}")

    safe_name = test_name.lower().replace(" ", "_").replace("/", "_")
    cm_path = os.path.join(model_dir, f"{safe_name}_manual_test_confusion_matrix.png")

    save_confusion_matrix_image(
        y_test,
        y_pred,
        f"{test_name} Manual Test",
        cm_path,
    )

    detail_df = pd.DataFrame(
        {
            "filename": filenames,
            "true_label": y_test.values,
            "pred_label": y_pred,
            "ai_probability": y_prob,
            "correct": y_test.values == y_pred,
        }
    )

    detail_csv = os.path.join(model_dir, f"{safe_name}_manual_test_predictions.csv")
    detail_df.to_csv(detail_csv, index=False, encoding="utf-8-sig")

    print(f"Confusion matrix image saved: {cm_path}")
    print(f"Prediction detail saved: {detail_csv}")

    return {
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": cm,
        "classification_report": report,
        "confusion_matrix_image": cm_path,
        "detail_csv": detail_csv,
    }


# ============================================================
# 7. 학습 실행
# ============================================================

run_context = mlflow.start_run() if USE_MLFLOW else nullcontext()

with run_context:
    if USE_MLFLOW:
        mlflow.log_params(
            {
                "model_type": "RandomForest",
                "n_estimators": n_estimators,
                "max_depth": max_depth,
                "min_samples_split": min_samples_split,
                "min_samples_leaf": min_samples_leaf,
                "random_state": 42,
                "class_weight": "balanced",
                "added_features": ",".join(added_features),
                "existing_added_features": ",".join(existing_added_features),
                "missing_added_features": ",".join(missing_added_features),
                "model_mode": "new_features_only",
                "feature_count": len(final_columns),
            }
        )

    # ------------------------------------------------------------
    # 추가 feature 3개가 포함된 최종 모델 학습
    # ------------------------------------------------------------

    final_result = train_and_evaluate(
        X_train,
        X_valid,
        y_train,
        y_valid,
        "Metadata Model with 3 Added Features",
    )

    if USE_MLFLOW:
        mlflow.log_metric("accuracy", final_result["accuracy"])
        mlflow.log_metric("precision", final_result["precision"])
        mlflow.log_metric("recall", final_result["recall"])
        mlflow.log_metric("f1", final_result["f1"])

    # ------------------------------------------------------------
    # Validation 결과 저장
    # ------------------------------------------------------------

    result_df = pd.DataFrame(
        [
            {
                "model": "metadata_model_with_3_added_features",
                "accuracy": final_result["accuracy"],
                "precision": final_result["precision"],
                "recall": final_result["recall"],
                "f1": final_result["f1"],
                "feature_count": len(final_columns),
            }
        ]
    )

    result_csv = os.path.join(model_dir, "metadata_model_result.csv")
    result_df.to_csv(result_csv, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 70)
    print("Validation Result")
    print("=" * 70)
    print(result_df)

    # ------------------------------------------------------------
    # Feature Importance 저장
    # ------------------------------------------------------------

    final_model = final_result["model"]

    feat_df = pd.DataFrame(
        {
            "feature": X_train.columns,
            "importance": final_model.feature_importances_,
        }
    ).sort_values(by="importance", ascending=False)

    feat_csv = os.path.join(model_dir, "feature_importance.csv")
    feat_df.to_csv(feat_csv, index=False, encoding="utf-8-sig")

    # ------------------------------------------------------------
    # 최종 모델 / 컬럼 저장
    # ------------------------------------------------------------

    model_path = os.path.join(model_dir, "rf_metadata_model.pkl")
    cols_path = os.path.join(model_dir, "model_columns.pkl")

    joblib.dump(final_model, model_path)
    joblib.dump(X_train.columns.tolist(), cols_path)

    # ------------------------------------------------------------
    # train_datasets/test 폴더 평가
    # ------------------------------------------------------------

    manual_test_result = evaluate_manual_test_folder(
        final_model,
        X_train.columns.tolist(),
        "Metadata Model with 3 Added Features",
    )

    # ------------------------------------------------------------
    # MLflow artifact 저장
    # ------------------------------------------------------------

    if USE_MLFLOW:
        mlflow.sklearn.log_model(final_model, "rf_model")

        mlflow.log_artifact(
            cols_path,
            artifact_path=MLFLOW_COLUMNS_ARTIFACT_DIR,
        )

        mlflow.log_artifact(
            feat_csv,
            artifact_path=MLFLOW_COLUMNS_ARTIFACT_DIR,
        )

        mlflow.log_artifact(
            result_csv,
            artifact_path=MLFLOW_COLUMNS_ARTIFACT_DIR,
        )

        mlflow.log_artifact(
            final_result["confusion_matrix_image"],
            artifact_path=MLFLOW_COLUMNS_ARTIFACT_DIR,
        )

        if manual_test_result is not None:
            mlflow.log_artifact(
                manual_test_result["confusion_matrix_image"],
                artifact_path=MLFLOW_COLUMNS_ARTIFACT_DIR,
            )
            mlflow.log_artifact(
                manual_test_result["detail_csv"],
                artifact_path=MLFLOW_COLUMNS_ARTIFACT_DIR,
            )

    print(
        f"\nTraining complete\n"
        f"- USE_MLFLOW: {USE_MLFLOW}\n"
        f"- final model: {model_path}\n"
        f"- columns: {cols_path}\n"
        f"- importance: {feat_csv}\n"
        f"- validation result: {result_csv}\n"
        f"- validation confusion matrix image: {final_result['confusion_matrix_image']}"
    )

    if manual_test_result is not None:
        print(
            f"- manual test confusion matrix image: "
            f"{manual_test_result['confusion_matrix_image']}"
        )
        print(
            f"- manual test predictions: "
            f"{manual_test_result['detail_csv']}"
        )