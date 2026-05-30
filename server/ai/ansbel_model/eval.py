import os
import joblib
import numpy as np

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
    개별 모델 predict가 실패해도 검증 전체가 멈추지 않도록 처리.
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
    이 결과 리스트는 build_feature_vector()에 들어간다.
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


def build_validation_dataset():
    """
    val_ai, val_real 폴더에서 이미지를 읽고 검증용 X, y를 만든다.

    label:
    - AI 이미지: 1
    - Real 이미지: 0
    """

    samples = []

    samples.extend(collect_image_paths(VAL_AI_DATA_DIR, label=1))
    samples.extend(collect_image_paths(VAL_REAL_DATA_DIR, label=0))

    if not samples:
        print("[오류] 검증할 이미지가 없습니다.")
        print(f"AI 검증 이미지 폴더: {VAL_AI_DATA_DIR}")
        print(f"Real 검증 이미지 폴더: {VAL_REAL_DATA_DIR}")
        return None, None, None

    ai_count = sum(1 for _, label in samples if label == 1)
    real_count = sum(1 for _, label in samples if label == 0)

    print()
    print("=== Validation Dataset Info ===")
    print(f"총 이미지 수: {len(samples)}")
    print(f"AI 이미지 수: {ai_count}")
    print(f"Real 이미지 수: {real_count}")
    print(f"Feature order: {FEATURE_ORDER}")
    print()

    X = []
    y = []
    image_paths = []

    for index, (image_path, label) in enumerate(samples, start=1):
        print(f"[{index}/{len(samples)}] 처리 중: {image_path}")

        try:
            image_bytes = read_image_bytes(image_path)

            individual_results = predict_individual_models(image_bytes)
            features = build_feature_vector(individual_results)

            X.append(features)
            y.append(label)
            image_paths.append(image_path)

            print(f"  features: {features}")
            print(f"  label: {label}")

        except Exception as e:
            print(f"  [스킵] 이미지 처리 실패: {image_path}")
            print(f"  reason: {e}")

    if not X:
        print("[오류] 모든 검증 이미지 처리에 실패했습니다.")
        return None, None, None

    return (
        np.array(X, dtype=float),
        np.array(y, dtype=int),
        image_paths,
    )


def load_individual_models():
    """
    5개 개별 모델을 메모리에 로드한다.
    """

    print("=== Load Individual Models ===")

    load_forensic_analysis()
    load_meta_data()
    load_visual_anomaly()
    load_external_search()
    load_water_mark()

    print("Individual models loaded.")


def load_ensemble_model():
    """
    저장된 ensemble_model.pkl을 로드한다.
    """

    if not os.path.exists(MODEL_SAVE_PATH):
        print("[오류] 앙상블 모델 파일이 없습니다.")
        print(f"찾는 위치: {MODEL_SAVE_PATH}")
        print("먼저 학습 파일을 실행해서 ensemble_model.pkl을 생성해야 합니다.")
        return None

    model = joblib.load(MODEL_SAVE_PATH)

    print()
    print("=== Ensemble Model Loaded ===")
    print(f"Model path: {MODEL_SAVE_PATH}")

    return model


def validate_model():
    """
    저장된 앙상블 모델을 불러와 val_ai, val_real 데이터셋으로 검증한다.
    """

    load_individual_models()

    model = load_ensemble_model()

    if model is None:
        return

    X_val, y_val, image_paths = build_validation_dataset()

    if X_val is None or y_val is None:
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

    for i, image_path in enumerate(image_paths):
        filename = os.path.basename(image_path)

        if y_prob is not None:
            print(
                f"[{i + 1}] file={filename}, true={y_val[i]}, pred={y_pred[i]}, ai_prob={y_prob[i]:.4f}"
            )
        else:
            print(
                f"[{i + 1}] file={filename}, true={y_val[i]}, pred={y_pred[i]}"
            )


if __name__ == "__main__":
    validate_model()