import os
import joblib
import numpy as np

_model = None

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "ensemble_model.pkl")

# 학습/추론 feature 순서 고정
FEATURE_ORDER = [
    "Water Mark",
    "Meta Data",
    "external_search",
    "forensic_analysis",
    "Visual anomaly",
]

# 혹시 model_name 표기가 다르게 들어올 경우 대비
MODEL_NAME_ALIASES = {
    "Water Mark": "Water Mark",
    "water_mark": "Water Mark",
    "watermark": "Water Mark",

    "Meta Data": "Meta Data",
    "meta_data": "Meta Data",
    "metadata": "Meta Data",

    "external_search": "external_search",
    "External Search": "external_search",

    "forensic_analysis": "forensic_analysis",
    "Forensic Analysis": "forensic_analysis",

    "Visual anomaly": "Visual anomaly",
    "visual_anomaly": "Visual anomaly",
    "Visual Anomaly": "Visual anomaly",
}


def load_model():
    """
    서버 시작 시 또는 최초 예측 시 앙상블 모델을 로드한다.
    """
    global _model

    if _model is not None:
        return _model

    print("Loading Logistic Regression Meta-Model...")

    if not os.path.exists(MODEL_PATH):
        print(
            f"-> WARNING: {MODEL_PATH} not found. "
            "Please run train.py first. Will fallback to average logic."
        )
        return None

    _model = joblib.load(MODEL_PATH)
    print("-> Ensemble model loaded successfully.")

    return _model


def normalize_confidence(value):
    """
    confidence 값을 항상 0~1 범위로 변환한다.

    예:
    0.4129   -> 0.4129
    42.64    -> 0.4264
    "42.64%" -> 0.4264
    """

    if value is None:
        return 0.0

    value = str(value).replace("%", "").strip()

    try:
        number = float(value)
    except ValueError:
        return 0.0

    if number > 1:
        number = number / 100

    return min(max(number, 0.0), 1.0)


def normalize_model_name(model_name):
    """
    개별 모델 결과의 model_name을 FEATURE_ORDER에 맞는 이름으로 정규화한다.
    """

    if model_name is None:
        return None

    return MODEL_NAME_ALIASES.get(model_name, model_name)


def build_feature_vector(individual_results):
    """
    개별 모델 결과 리스트를 로지스틱 회귀 입력 feature 5개로 변환한다.

    반환 순서:
    [Water Mark, Meta Data, external_search, forensic_analysis, Visual anomaly]
    """

    features_by_name = {name: 0.0 for name in FEATURE_ORDER}

    for result in individual_results:
        if not isinstance(result, dict):
            continue

        raw_name = result.get("model_name")
        model_name = normalize_model_name(raw_name)

        if model_name not in features_by_name:
            print(f"[WARNING] Unknown model_name ignored: {raw_name}")
            continue

        confidence = normalize_confidence(result.get("confidence", 0.0))
        features_by_name[model_name] = confidence

    features = [features_by_name[name] for name in FEATURE_ORDER]

    return features


def fallback_average_prediction(features):
    """
    ensemble_model.pkl이 없거나 예측 중 에러가 발생했을 때 사용하는 단순 평균 방식.
    """

    final_confidence = sum(features) / max(len(features), 1)
    predicted_idx = 1 if final_confidence >= 0.5 else 0

    return predicted_idx, final_confidence


def predict(individual_results: list) -> dict:
    """
    5개의 개별 하위 모델 결과를 기반으로 로지스틱 회귀 예측을 수행한다.

    individual_results 예시:
    [
        {"model_name": "Visual anomaly", "predicted_idx": 0, "confidence": 0.0778},
        {"model_name": "external_search", "predicted_idx": 0, "confidence": 0},
        {"model_name": "forensic_analysis", "predicted_idx": 1, "confidence": 0.5},
        {"model_name": "Meta Data", "predicted_idx": 0, "confidence": 0.4129},
        {"model_name": "Water Mark", "predicted_idx": 0, "confidence": 0}
    ]
    """

    model = load_model()

    print("Meta-Model evaluating base predictions...")

    features = build_feature_vector(individual_results)

    predicted_idx = 0
    final_confidence = 0.0
    used_fallback = False

    if model is not None:
        try:
            X = np.array([features], dtype=float)

            predicted_idx = int(model.predict(X)[0])
            probabilities = model.predict_proba(X)[0]

            # model.classes_ 순서가 항상 [0, 1]이라는 보장이 없으므로 안전하게 인덱스 찾기
            class_index = np.where(model.classes_ == predicted_idx)[0][0]
            final_confidence = float(probabilities[class_index])

        except Exception as e:
            print(f"Ensemble prediction error: {e}")
            predicted_idx, final_confidence = fallback_average_prediction(features)
            used_fallback = True
    else:
        predicted_idx, final_confidence = fallback_average_prediction(features)
        used_fallback = True

    final_prediction_text = "AI Generated" if predicted_idx == 1 else "Real"

    return {
        "prediction": final_prediction_text,
        "predicted_idx": predicted_idx,
        "confidence": f"{final_confidence * 100:.2f}%",
        "description": (
            "Calculated by Logistic Regression Meta-Model."
            if not used_fallback
            else "Calculated by fallback average logic."
        ),
        "input_features": features,
        "feature_order": FEATURE_ORDER,
    }