# 데이터 관리 가이드

## 🎯 구글 드라이브 → 로컬 프로젝트 연동 방법

### 방법 1: 수동 복사 (권장 - 초보자용)

**단계:**

1. **구글 드라이브에서 다운로드**
   - 브라우저에서 구글 드라이브 접속
   - "AI Media Detector - 데이터" 폴더 찾기
   - 이미지 폴더 우클릭 → "다운로드"
   - 압축 파일이 다운로드됨

2. **프로젝트 폴더로 복사**
   ```
   다운로드한 압축 파일 압축 해제
   ↓
   ai_generated 폴더 → data/raw/image/ai_generated/
   real 폴더 → data/raw/image/real/
   ```

3. **검증**
   ```bash
   python scripts/verify_data.py
   ```

### 방법 2: 구글 드라이브 데스크톱 앱 (자동 동기화)

**장점**: 팀원들이 자동으로 최신 데이터 유지

**단계:**

1. **구글 드라이브 데스크톱 설치**
   - https://www.google.com/drive/download/ 접속
   - "Drive for desktop" 다운로드 및 설치

2. **동기화 설정**
   - 구글 드라이브 앱 실행
   - "AI Media Detector - 데이터" 폴더 우클릭
   - "오프라인에서 사용 가능하도록 설정"

3. **심볼릭 링크 생성 (선택)**
   ```cmd
   # 관리자 권한 CMD에서 실행
   mklink /D "C:\Users\dhlee\OneDrive\바탕 화면\ai-media-detector\data\raw\image" "G:\내 드라이브\AI Media Detector - 데이터\images"
   ```

## 📁 데이터 디렉토리 구조

```
data/
├── raw/                        # 원본 데이터 (수정 금지!)
│   ├── text/
│   │   ├── ai_generated/
│   │   │   ├── chatgpt_samples.json
│   │   │   └── hc3_dataset.json
│   │   └── human_written/
│   │       ├── cnn_articles.json
│   │       └── wiki_texts.json
│   └── image/
│       ├── ai_generated/       # 구글 드라이브에서 복사
│       │   ├── img_0001.png
│       │   ├── img_0002.png
│       │   └── ...
│       └── real/               # 구글 드라이브에서 복사
│           ├── img_0001.jpg
│           ├── img_0002.jpg
│           └── ...
├── processed/                  # 전처리 완료 (코드가 자동 생성)
│   ├── text/
│   │   └── cleaned_text.csv
│   └── image/
│       ├── resized_224x224/
│       └── augmented/
└── splits/                     # Train/Valid/Test 분할 (코드가 자동 생성)
    ├── train.txt
    ├── valid.txt
    └── test.txt
```

## 🔄 데이터 작업 워크플로우

### 초기 설정 (1회만)

```bash
# 1. 디렉토리 생성
python scripts/setup_directories.py

# 2. 구글 드라이브에서 이미지 복사 (수동)
# data/raw/image/ai_generated/ 에 복사
# data/raw/image/real/ 에 복사

# 3. 데이터 검증
python scripts/verify_data.py
```

### 일반 작업 흐름

```bash
# 1. 최신 데이터 확인
python scripts/verify_data.py

# 2. 전처리 실행 (이미지 리사이즈, 정규화 등)
python src/data/preprocessing/preprocess_images.py

# 3. 데이터 분할 (train/valid/test)
python src/data/preprocessing/split_dataset.py

# 4. 통계 리포트 생성
python src/data/preprocessing/generate_stats.py
```

## ⚠️ 주의사항

### 절대 하지 말아야 할 것

1. **`data/raw/` 폴더의 파일을 직접 수정하지 마세요**
   - 항상 복사본으로 작업
   - 원본은 백업용

2. **대용량 데이터를 Git에 커밋하지 마세요**
   - `.gitignore`에 `data/` 폴더가 포함되어 있음
   - 실수로 커밋하면 레포지토리가 망가짐

3. **구글 드라이브 용량 확인**
   - 15GB 무료 용량 초과 시 정리 필요
   - 압축 파일로 보관하여 용량 절약

### 권장사항

1. **주 1회 백업**
   - 중요한 시점마다 구글 드라이브에 백업
   - 파일명: `backup_YYYYMMDD.zip`

2. **버전 관리**
   - 데이터 수정 시 버전 기록
   - `docs/data_changelog.md` 업데이트

3. **팀 동기화**
   - 데이터 추가/삭제 시 팀 채팅에 공지
   - 특히 전처리 로직 변경 시 알림

## 🛠 문제 해결

### 문제: "폴더가 비어있습니다"

**원인**: 구글 드라이브에서 복사 안 함

**해결**:
1. 구글 드라이브 확인
2. 이미지 다운로드
3. `data/raw/image/` 폴더에 복사

### 문제: "용량이 너무 큽니다"

**해결**:
1. 일부만 사용 (1000개씩)
2. 압축 파일로 보관
3. 필요할 때만 압축 해제

### 문제: "경로를 찾을 수 없습니다"

**원인**: 폴더 구조가 다름

**해결**:
```bash
python scripts/setup_directories.py
```

## 📊 데이터 품질 체크리스트

- [ ] 이미지 개수: AI 생성 ≥ 1000, 실제 ≥ 1000
- [ ] 클래스 균형: ±10% 이내
- [ ] 이미지 포맷: PNG 또는 JPG
- [ ] 파일명 규칙: `img_XXXX.ext`
- [ ] 중복 이미지 없음
- [ ] 손상된 파일 없음

체크 명령어:
```bash
python scripts/verify_data.py
```