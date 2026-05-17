import os
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

from ai.water_mark.predict import predict as predict_water_mark
from ai.meta_data.predict import predict as predict_meta_data
from ai.external_search.predict import predict as predict_external_search
from ai.forensic_analysis.predict import predict as predict_forensic_analysis
from ai.visual_anomaly.predict import predict as predict_visual_anomaly

from ai.water_mark.predict import load_model as load_water_mark
from ai.meta_data.predict import load_model as load_meta_data
from ai.external_search.predict import load_model as laod_external_search
from ai.forensic_analysis.predict import load_model as load_forensic_analysis
from ai.visual_anomaly.predict import load_model as load_visual_anomaly


from ai.ansbel_model.predict import build_feature_vector, FEATURE_ORDER


BASE_DIR = os.path.dirname(__file__)

AI_DATA_DIR = os.path.join(BASE_DIR, "data", "ai")
REAL_DATA_DIR = os.path.join(BASE_DIR, "data", "real")

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
        samples.append((image_path, label))

    return samples


def safe_run_predict(predict_func, image_bytes, model_name):
    """
    개별 모델 predict가 실패해도 학습 전체가 멈추지 않도록 처리.
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


def build_training_dataset():
    samples = []

    samples.extend(collect_image_paths(AI_DATA_DIR, label=1))
    samples.extend(collect_image_paths(REAL_DATA_DIR, label=0))

    if not samples:
        print("[오류] 학습할 이미지가 없습니다.")
        print(f"AI 이미지 폴더: {AI_DATA_DIR}")
        print(f"Real 이미지 폴더: {REAL_DATA_DIR}")
        return None, None

    ai_count = sum(1 for _, label in samples if label == 1)
    real_count = sum(1 for _, label in samples if label == 0)

    print("=== Dataset Info ===")
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
        print("[오류] 모든 이미지 예측에 실패했습니다.")
        return None, None

    return np.array(X, dtype=float), np.array(y, dtype=int)


def train_meta_model():
    
    load_forensic_analysis()
    load_meta_data()
    load_visual_anomaly()
    laod_external_search()
    load_water_mark()
    
    X, y = build_training_dataset()

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


if __name__ == "__main__":
    train_meta_model()