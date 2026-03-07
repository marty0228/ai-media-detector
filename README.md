# AI Media Detector

AI 생성 텍스트 및 이미지를 감별하는 시스템

## 🚀 빠른 시작 (팀원용)

### 1. 레포지토리 클론

```bash
git clone https://github.com/marty0228/ai-media-detector.git
cd ai-media-detector
```

### 2. 환경 설정

```bash
# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 필수 패키지 설치
pip install -r requirements.txt
```

### 3. 프로젝트 구조 생성

```bash
python scripts/setup_directories.py
```

### 4. 데이터 준비

**방법 1: 구글 드라이브에서 수동 복사 (권장)**

1. 팀 공유 구글 드라이브 접속
2. "AI Media Detector - 데이터" 폴더에서 이미지 다운로드
3. 압축 해제 후 다음 위치에 복사:
   - AI 이미지 → `data/raw/image/ai_generated/`
   - 실제 이미지 → `data/raw/image/real/`

**방법 2: 구글 드라이브 데스크톱 앱 (자동 동기화)**

[docs/data_management.md](docs/data_management.md) 참고

### 5. 데이터 검증

```bash
python scripts/verify_data.py
```

성공 시 출력:
```
✅ AI 생성 이미지: 1000개
✅ 실제 이미지: 1000개
📊 데이터 통계 요약 ...
```

### 6. 전처리 및 학습 시작

```bash
# 이미지 전처리
python src/data/preprocessing/preprocess_images.py

# 데이터 분할
python src/data/preprocessing/split_dataset.py

# (이후 단계는 팀원별 작업)
```

## 📁 프로젝트 구조

```
ai-media-detector/
├── data/                    # ⚠️ Git에 포함되지 않음
│   ├── raw/                # 원본 데이터 (구글 드라이브에서 복사)
│   ├── processed/          # 전처리 완료
│   └── splits/             # train/valid/test
├── data_samples/           # ✅ Git에 포함 (샘플)
├── models/                 # 학습된 모델
├── src/                    # 소스 코드
│   ├── data/              # 데이터 처리
│   ├── models/            # 모델 구현
│   ├── api/               # API
│   └── web/               # 웹 인터페이스
├── docs/                   # 문서
├── notebooks/              # 실험 노트북
├── scripts/                # 유틸리티 스크립트
└── tests/                  # 테스트
```

## 👥 팀원 역할

- **이동훈 (PM/데이터 총괄)**: 데이터 관리, 품질 검증
- **김재혁 (백엔드/프론트)**: API, 웹 인터페이스
- **최정흠 (이미지 모델)**: CV 모델 구현
- **김시형 (텍스트 모델)**: NLP 모델 구현

## 📚 주요 문서

- [데이터 관리 가이드](docs/data_management.md) ⭐ 필독!
- [데이터 출처](docs/data_sources.md)
- [주간 보고서](docs/weekly_reports/)

## 🆘 문제 해결

- 데이터 관련: [docs/data_management.md](docs/data_management.md)
- 이슈 트래킹: GitHub Issues
- 팀 문의: 디스코드/카카오톡

## 📝 개발 진행 상황

- [x] 프로젝트 구조 설정
- [x] 데이터 수집 계획 수립
- [ ] 데이터 전처리
- [ ] 베이스라인 모델 구축
- [ ] 모델 개선
- [ ] 웹 데모 구현