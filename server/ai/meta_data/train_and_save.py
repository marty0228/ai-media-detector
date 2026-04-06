import os, joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ---------------------------------------------------------
# 1. 학습을 위한 데이터 로딩 및 결측치 전처리
# ---------------------------------------------------------
print("모델 학습을 시작합니다...")
base_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(base_dir, 'model', 'metadata_dataset_expanded.csv')).dropna(subset=['label'])
df = df.fillna({'make_raw':'None', 'model_raw':'None', 'camera_brand':'none', 'software_raw':'None', 'software_type':'none'})
df['label'] = df['label'].astype(int)

# ---------------------------------------------------------
# 2. 모델 학습 피처(Feature) 분리 및 인코딩 프로세스
# ---------------------------------------------------------
# 정답 라벨과 단순 문자열 필드는 피처(입력값) 구조에서 제외
X = df.drop(columns=['label', 'filename', 'make_raw', 'model_raw', 'software_raw'], errors='ignore')
y = df['label']

# 문자형 범주 카테고리 필드를 모델이 이해할 수 있는 숫자형(원-핫 인코딩)으로 일괄 변환
cat_cols = [c for c in ['camera_brand', 'software_type'] if c in X.columns]
if cat_cols: X = pd.get_dummies(X, columns=cat_cols)
X = X.astype({c: int for c in X.columns if X[c].dtype == 'bool'})

# ---------------------------------------------------------
# 3. 모델 정의 및 분할 훈련 (Train/Validation)
# ---------------------------------------------------------
X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

model = RandomForestClassifier(
  n_estimators=300, 
  max_depth=10, 
  min_samples_split=4, 
  min_samples_leaf=2, 
  random_state=42, 
  class_weight='balanced'
  )
model.fit(X_train, y_train)

# ---------------------------------------------------------
# 4. 검증 성능 리포팅 및 중요 피처(Importance) 추출 구조
# ---------------------------------------------------------
y_pred = model.predict(X_valid)
print(f"\n검증 Accuracy: {accuracy_score(y_valid, y_pred):.4f}\n\nConfusion Matrix:\n{confusion_matrix(y_valid, y_pred)}\n\nClassification Report:\n{classification_report(y_valid, y_pred, digits=4)}")

feat_df = pd.DataFrame({'feature': X_train.columns, 'importance': model.feature_importances_}).sort_values(by='importance', ascending=False)
feat_csv = os.path.join(base_dir, 'model', 'feature_importance.csv')
feat_df.to_csv(feat_csv, index=False, encoding='utf-8-sig')

# ---------------------------------------------------------
# 5. 최종 완성 모델 직렬화 및 구조 저장 내보내기 (.pkl)
# ---------------------------------------------------------
model_path, cols_path = os.path.join(base_dir, 'model', 'rf_metadata_model.pkl'), os.path.join(base_dir, 'model', 'model_columns.pkl')
joblib.dump(model, model_path)
joblib.dump(X_train.columns.tolist(), cols_path)

print(f"\n학습 완료\n- 모델: {model_path}\n- 컬럼: {cols_path}\n- 중요도: {feat_csv}")