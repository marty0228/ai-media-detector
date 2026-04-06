import os
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

# ── 설정 변수 ──
DATA_FILE = os.path.join(os.path.dirname(__file__), "dataset.txt")
MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), "ensemble_model.pkl")

def train_meta_model():
    print("Checking for dataset.txt...")
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} 파일을 찾을 수 없습니다.")
        print("훈련 데이터를 'dataset.txt'라는 이름으로 만들어주세요.")
        print("형식 (공백 구분): 워터마크 메타데이터 외부검색 포렌식 시각적이상 라벨")
        print("예시: 0.3 0.2 0.34 0.7 0.2 1")
        return

    print("Loading data...")
    try:
        # 데이터 로딩 (모든 값이 숫자로 이루어져 있다고 가정)
        data = np.loadtxt(DATA_FILE)
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return

    # 1줄만 있을 경우 2차원 배열로 차원 맞춰주기
    if len(data.shape) == 1:
        data = data.reshape(1, -1)

    # 6개의 컬럼이 아니면 오류
    if data.shape[1] < 6:
        print(f"Error: 데이터 형식이 잘못되었습니다. (기대 컬럼 6개, 현재 {data.shape[1]}개)")
        return

    # 피처(X) 5개와 타겟(y) 1개로 분리
    X = data[:, :5]
    y = data[:, 5]

    print(f"Loaded {X.shape[0]} samples.")
    print("Training Logistic Regression model...")

    # 데이터 클래스 종류 확인 (AI=1, Real=0 두 종류가 다 있어야 함)
    unique_classes = np.unique(y)
    if len(unique_classes) < 2:
        print("\n[오류] 훈련을 진행할 수 없습니다!")
        print(f"데이터셋에 오직 하나의 클래스({unique_classes[0]})만 존재합니다.")
        print("로지스틱 회귀로 앙상블을 학습하려면 'AI(1)' 데이터와 '진짜(0)' 데이터가 최소 1개씩은 있어야 비교군(결정 경계)을 만들 수 있습니다.")
        print("dataset.txt 파일의 마지막 줄에 라벨이 0인 데이터를 추가해 주세요.\n")
        return

    # 두 클래스의 비율 차이를 보정하기 위해 class_weight='balanced' 설정
    model = LogisticRegression(class_weight='balanced')
    model.fit(X, y)

    print("--- Training completed ---")
    print(f"Model coefficients (Weights): {model.coef_[0]}")
    print(f"Model intercept: {model.intercept_[0]}")

    # 모델을 pkl 형태로 저장
    joblib.dump(model, MODEL_SAVE_PATH)
    print(f"Model saved successfully to {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    train_meta_model()
