import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

base_dir = os.path.dirname(os.path.abspath(__file__))

print("모델 학습을 시작합니다...")

# 확장된 feature CSV 경로
csv_path = os.path.join(base_dir, 'model', 'metadata_dataset_expanded.csv')
df = pd.read_csv(csv_path)

# -----------------------------
# 1. 기본 전처리
# -----------------------------
# 문자열 None/결측치 정리
df = df.fillna({
    'make_raw': 'None',
    'model_raw': 'None',
    'camera_brand': 'none',
    'software_raw': 'None',
    'software_type': 'none'
})

# label 없는 행 제거
df = df.dropna(subset=['label'])

# label을 정수형으로 맞춤
df['label'] = df['label'].astype(int)

# -----------------------------
# 2. 학습에 쓸 feature 선택
# -----------------------------
# 제외할 컬럼:
# - label: 타깃
# - filename: 파일명이라 일반화에 도움 적음
# - raw 문자열 컬럼: 그대로 넣으면 랜덤포레스트가 못 씀
drop_columns = [
    'label',
    'filename',
    'make_raw',
    'model_raw',
    'software_raw'
]

existing_drop_columns = [col for col in drop_columns if col in df.columns]

X = df.drop(columns=existing_drop_columns)
y = df['label']

# 범주형 컬럼만 원-핫 인코딩
categorical_cols = [col for col in ['camera_brand', 'software_type'] if col in X.columns]
X = pd.get_dummies(X, columns=categorical_cols)

# 혹시 bool 타입이 있으면 int로 변환
for col in X.columns:
    if X[col].dtype == 'bool':
        X[col] = X[col].astype(int)

# -----------------------------
# 3. train / valid 분리
# -----------------------------
X_train, X_valid, y_train, y_valid = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# -----------------------------
# 4. 모델 생성 및 학습
# -----------------------------
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_split=4,
    min_samples_leaf=2,
    random_state=42,
    class_weight='balanced'
)

model.fit(X_train, y_train)

# -----------------------------
# 5. 검증 성능 확인
# -----------------------------
y_pred = model.predict(X_valid)

acc = accuracy_score(y_valid, y_pred)
print(f"\n검증 Accuracy: {acc:.4f}")

print("\nConfusion Matrix:")
print(confusion_matrix(y_valid, y_pred))

print("\nClassification Report:")
print(classification_report(y_valid, y_pred, digits=4))

# -----------------------------
# 6. Feature Importance 저장
# -----------------------------
feature_importance_df = pd.DataFrame({
    'feature': X_train.columns,
    'importance': model.feature_importances_
}).sort_values(by='importance', ascending=False)

importance_csv_path = os.path.join(base_dir, 'model', 'feature_importance.csv')
feature_importance_df.to_csv(importance_csv_path, index=False, encoding='utf-8-sig')

print("\n상위 20개 중요 feature:")
print(feature_importance_df.head(20))

# -----------------------------
# 7. 모델 및 컬럼 정보 저장
# -----------------------------
model_path = os.path.join(base_dir, 'model', 'rf_metadata_model.pkl')
columns_path = os.path.join(base_dir, 'model', 'model_columns.pkl')

joblib.dump(model, model_path)
joblib.dump(X_train.columns.tolist(), columns_path)

print(f"\n학습 완료")
print(f"- 모델 저장: {model_path}")
print(f"- 컬럼 정보 저장: {columns_path}")
print(f"- feature importance 저장: {importance_csv_path}")