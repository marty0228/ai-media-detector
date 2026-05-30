import os
import joblib
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

from ai.water_mark.predict import predict as predict_water_mark
from ai.meta_data.predict import predict as predict_meta_data
from ai.external_search.predict import predict as predict_external_search
from ai.forensic_analysis.predict import predict as predict_forensic_analysis
from ai.visual_anomaly.predict import predict as predict_visual_anomaly

from ai.water_mark.predict import load_model as load_water_mark
from ai.meta_data.predict import load_model as load_meta_data
from ai.external_search.predict import load_model as load_external_search
from ai.forensic_analysis.predict import load_model as load_forensic_analysis
from ai.visual_anomaly.predict import load_model as load_visual_anomaly

from ai.ansbel_model.predict import build_feature_vector, FEATURE_ORDER


BASE_DIR = os.path.dirname(__file__)

# 학습 데이터 폴더
AI_DATA_DIR = os.path.join(BASE_DIR, "data", "ai")
REAL_DATA_DIR = os.path.join(BASE_DIR, "data", "real")

# 검증 데이터 폴더
VAL_AI_DATA_DIR = os.path.join(BASE_DIR, "data", "val_ai")
VAL_REAL_DATA_DIR = os.path.join(BASE_DIR, "data", "val_real")

MODEL_SAVE_PATH = os.path.join(BASE_DIR, "ensemble_model.pkl")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def is_image_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in IMAGE_EXTENSIONS


def read_image_bytes(image_path):
    with open(image_path, "rb") as f:
        return f.read()


def collect_image_paths(directory, label):
    samples = []

    if not os.path.exists(directory):
        print(f"[경고] 폴더가 없습니다: {directory}")
        return samples

    for filename in os.listdir(directory):
        if not is_image_file(filename):
            continue

        image_path = os.path.join(directory, filename)

        if os.path.isfile(image_path):
            samples.append((image_path, label))

    return samples


def safe_run_predict(predict_func, image_bytes, model_name):
    """
    개별 모델 predict가 실패해도 전체 학습/검증이 멈추지 않도록 처리.
    """

    try:
        result = predict_func(image_bytes)

        if isinstance(result, dict):
            result["model_name"] = result.get("model_name", model_name)
            return result

        return {
            "model_name": model_name,
            "predicted_idx": 0,
            "confidence": result,
        }

    except Exception as e:
        print(f"    [경고] {model_name} 예측 실패: {e}")

        return {
            "model_name": model_name,
            "predicted_idx": 0,
            "confidence": 0.0,
            "error": str(e),
        }


def predict_individual_models(image_bytes):
    """
    이미지 bytes를 받아 5개 하위 모델의 결과 리스트를 생성한다.
    이 결과 리스트는 ansbel_model.predict의 build_feature_vector()에 들어간다.
    """

    individual_results = [
        safe_run_predict(
            predict_water_mark,
            image_bytes,
            "Water Mark",
        ),
        safe_run_predict(
            predict_meta_data,
            image_bytes,
            "Meta Data",
        ),
        safe_run_predict(
            predict_external_search,
            image_bytes,
            "external_search",
        ),
        safe_run_predict(
            predict_forensic_analysis,
            image_bytes,
            "forensic_analysis",
        ),
        safe_run_predict(
            predict_visual_anomaly,
            image_bytes,
            "Visual anomaly",
        ),
    ]

    return individual_results


def build_dataset(ai_dir, real_dir, dataset_name="Dataset"):
    """
    ai_dir, real_dir 폴더에서 이미지를 읽고,
    각 이미지에 대해 5개 개별 모델의 출력값을 feature vector로 변환한다.

    label:
    - AI 이미지: 1
    - Real 이미지: 0
    """

    samples = []

    samples.extend(collect_image_paths(ai_dir, label=1))
    samples.extend(collect_image_paths(real_dir, label=0))

    if not samples:
        print(f"[오류] {dataset_name} 이미지가 없습니다.")
        print(f"AI 이미지 폴더: {ai_dir}")
        print(f"Real 이미지 폴더: {real_dir}")
        return None, None

    ai_count = sum(1 for _, label in samples if label == 1)
    real_count = sum(1 for _, label in samples if label == 0)

    print()
    print(f"=== {dataset_name} Info ===")
    print(f"총 이미지 수: {len(samples)}")
    print(f"AI 이미지 수: {ai_count}")
    print(f"Real 이미지 수: {real_count}")
    print(f"Feature order: {FEATURE_ORDER}")
    print()

    X = []
    y = []

    for index, (image_path, label) in enumerate(samples, start=1):
        print(f"[{index}/{len(samples)}] 처리 중: {image_path}")

        try:
            image_bytes = read_image_bytes(image_path)

            individual_results = predict_individual_models(image_bytes)
            features = build_feature_vector(individual_results)

            X.append(features)
            y.append(label)

            print(f"  features: {features}")
            print(f"  label: {label}")

        except Exception as e:
            print(f"  [스킵] 이미지 처리 실패: {image_path}")
            print(f"  reason: {e}")

    if not X:
        print(f"[오류] {dataset_name}의 모든 이미지 예측에 실패했습니다.")
        return None, None

    return np.array(X, dtype=float), np.array(y, dtype=int)


def evaluate_meta_model(model):
    """
    val_ai, val_real 폴더를 읽어서 학습된 앙상블 모델을 검증한다.
    """

    print()
    print("=== Validation Start ===")

    X_val, y_val = build_dataset(
        VAL_AI_DATA_DIR,
        VAL_REAL_DATA_DIR,
        dataset_name="Validation Dataset",
    )

    if X_val is None or y_val is None:
        print("[경고] 검증 데이터가 없어 검증을 건너뜁니다.")
        return

    unique_classes, counts = np.unique(y_val, return_counts=True)
    class_distribution = dict(zip(unique_classes, counts))

    print()
    print("=== Validation Data ===")
    print(f"X_val shape: {X_val.shape}")
    print(f"y_val shape: {y_val.shape}")
    print(f"Class distribution: {class_distribution}")

    if len(unique_classes) < 2:
        print()
        print("[경고] 검증 데이터에 한 클래스만 존재합니다.")
        print(f"현재 검증 클래스: {unique_classes}")
        print("val_ai와 val_real 폴더에 각각 최소 1개 이상의 이미지가 있어야 지표가 의미 있습니다.")

    y_pred = model.predict(X_val)

    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_val)[:, 1]
    else:
        y_prob = None

    accuracy = accuracy_score(y_val, y_pred)
    precision = precision_score(y_val, y_pred, zero_division=0)
    recall = recall_score(y_val, y_pred, zero_division=0)
    f1 = f1_score(y_val, y_pred, zero_division=0)

    cm = confusion_matrix(y_val, y_pred, labels=[0, 1])

    print()
    print("=== Validation Result ===")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-score : {f1:.4f}")

    print()
    print("Confusion Matrix")
    print("labels: 0=real, 1=ai")
    print("[[TN FP]")
    print(" [FN TP]]")
    print(cm)

    tn, fp, fn, tp = cm.ravel()

    print()
    print(f"TN: {tn}")
    print(f"FP: {fp}")
    print(f"FN: {fn}")
    print(f"TP: {tp}")

    print()
    print("Classification Report")
    print(
        classification_report(
            y_val,
            y_pred,
            labels=[0, 1],
            target_names=["real", "ai"],
            zero_division=0,
        )
    )

    print()
    print("=== Validation Samples ===")

    for i in range(len(y_val)):
        if y_prob is not None:
            print(
                f"[{i + 1}] true={y_val[i]}, pred={y_pred[i]}, ai_prob={y_prob[i]:.4f}"
            )
        else:
            print(
                f"[{i + 1}] true={y_val[i]}, pred={y_pred[i]}"
            )


def train_meta_model():
    """
    1. 개별 모델 로드
    2. data/ai, data/real로 앙상블 메타 모델 학습
    3. ensemble_model.pkl 저장
    4. data/val_ai, data/val_real로 검증
    """

    print("=== Load Individual Models ===")

    load_forensic_analysis()
    load_meta_data()
    load_visual_anomaly()
    load_external_search()
    load_water_mark()

    print("Individual models loaded.")

    X, y = build_dataset(
        AI_DATA_DIR,
        REAL_DATA_DIR,
        dataset_name="Training Dataset",
    )

    if X is None or y is None:
        return

    unique_classes, counts = np.unique(y, return_counts=True)
    class_distribution = dict(zip(unique_classes, counts))

    print()
    print("=== Training Data ===")
    print(f"X shape: {X.shape}")
    print(f"y shape: {y.shape}")
    print(f"Class distribution: {class_distribution}")

    if len(unique_classes) < 2:
        print()
        print("[오류] 훈련을 진행할 수 없습니다.")
        print(f"현재 데이터셋에는 클래스 {unique_classes[0]}만 존재합니다.")
        print("data/ai와 data/real 폴더에 각각 최소 1개 이상의 이미지가 필요합니다.")
        return

    print()
    print("Training Logistic Regression Meta-Model...")

    model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        random_state=42,
    )

    model.fit(X, y)

    print()
    print("--- Training completed ---")
    print(f"Feature order: {FEATURE_ORDER}")
    print(f"Model coefficients: {model.coef_[0]}")
    print(f"Model intercept: {model.intercept_[0]}")

    joblib.dump(model, MODEL_SAVE_PATH)

    print()
    print(f"Model saved successfully to: {MODEL_SAVE_PATH}")

    evaluate_meta_model(model)


if __name__ == "__main__":
    train_meta_model()