import os
import joblib

# 글로벌 변수로 모델을 하나만 띄워 유지
_model = None

def load_model():
    """서버 시작 시 앙상블 모델 로드"""
    global _model
    print("Loading Regression Meta-Model...")
    
    model_path = os.path.join(os.path.dirname(__file__), "ensemble_model.pkl")
    if os.path.exists(model_path):
        _model = joblib.load(model_path)
        print("-> Ensemble model (Logistic Regression) loaded successfully.")
    else:
        print(f"-> WARNING: {model_path} not found. Please run train.py! Will fallback to average logic.")


def predict(individual_results: list) -> dict:
    """
    5개의 개별 하위 모델 결과를 기반으로 로지스틱 회귀 예측을 수행
    """
    global _model
    
    if _model is None:
        load_model()
        
    print("Meta-Model evaluating base predictions...")

    # 학습 순서 지정: 워터마크 -> 메타데이터 -> 외부검색 -> 포렌식 -> 시각적이상
    # (결과가 어떤 순서로 들어오든 이 순서로 피쳐 벡터를 생성되도록 함)
    model_mapping = {
        "Water Mark": 0,
        "Meta Data": 1,
        "external_search": 2,
        "Model 5": 3,
        "visual_anomaly": 4
    }
    
    # 기본값 0.0으로 5개 배열 초기화
    features = [0.0, 0.0, 0.0, 0.0, 0.0]
    
    for res in individual_results:
        name = res.get("model_name")
        conf = res.get("confidence", 0.0)
        
        if name in model_mapping:
            idx = model_mapping[name]
            # conf가 혹시 문자열일수도 있으므로 float 형변환
            features[idx] = float(conf)
            
    # 모델로 예측 진행
    if _model is not None:
        try:
            # predict_proba 반환 형태: [[클래스0확률, 클래스1확률]]
            prob = _model.predict_proba([features])[0]
            
            # 클래스가 1개(예제 한종류 훈련)만 있으면 확률이 [1.0]으로 나옴
            if len(prob) > 1:
                ai_prob = prob[1] # 클래스 1 (AI) 일 확률
            else:
                ai_prob = 1.0 if _model.classes_[0] == 1 else 0.0
                
            predicted_idx = 1 if ai_prob >= 0.5 else 0
            final_confidence = ai_prob
        except Exception as e:
            print(f"Ensemble prediction error: {e}")
            # 에러 발생 시 단순 평균 폴백
            final_confidence = sum(features) / len(features)
            predicted_idx = 1 if final_confidence >= 0.5 else 0
    else:
        # 모델(.pkl) 파일이 없으면 안전장치로 단순 평균 사용
        final_confidence = sum(features) / max(len(features), 1)
        predicted_idx = 1 if final_confidence >= 0.5 else 0

    final_prediction_text = "AI Generated" if predicted_idx == 1 else "Real"
    
    return {
        "prediction": final_prediction_text,
        "predicted_idx": predicted_idx,
        # 프론트엔드가 퍼센트(%) 포맷을 변환하므로 기존 인터페이스 유지
        "confidence": f"{final_confidence * 100:.2f}%", 
        "description": "Calculated by Logistic Regression Meta-Model.",
        # 디버그/로깅 용도로 넘겨줌
        "input_features": features
    }
