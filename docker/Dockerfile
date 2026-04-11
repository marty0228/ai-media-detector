# 가벼운 파이썬 환경 사용
FROM python:3.9-slim

# MLflow와 GCP 연동에 필요한 라이브러리 설치
RUN pip install mlflow psycopg2-binary google-cloud-storage

# Cloud Run의 기본 포트인 8080 노출
EXPOSE 8080

# 컨테이너가 켜질 때 실행될 명령어 (환경 변수는 Cloud Run에서 주입)
CMD mlflow server \
  --host 0.0.0.0 \
  --port 8080 \
  --backend-store-uri $BACKEND_STORE_URI \
  --default-artifact-root $ARTIFACT_ROOT