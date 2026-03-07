"""
프로젝트 디렉토리 구조를 자동으로 생성하는 스크립트
최초 1회 실행: python scripts/setup_directories.py
"""
import os
from pathlib import Path

def create_directory_structure():
    base_dir = Path(__file__).parent.parent
    
    directories = [
        # 데이터 디렉토리 (Git에서 제외, 로컬에만 존재)
        "data/raw/text/ai_generated",
        "data/raw/text/human_written",
        "data/raw/image/ai_generated",
        "data/raw/image/real",
        "data/processed/text",
        "data/processed/image",
        "data/splits",
        
        # 샘플 데이터 (Git에 포함)
        "data_samples/text",
        "data_samples/image/ai_sample_10",
        "data_samples/image/real_sample_10",
        
        # 모델 디렉토리
        "models/text",
        "models/image",
        "models/checkpoints",
        
        # 소스 코드
        "src/data/collectors",
        "src/data/preprocessing",
        "src/models/text",
        "src/models/image",
        "src/api",
        "src/web/templates",
        "src/web/static",
        
        # 문서
        "docs/weekly_reports",
        "docs/experiments",
        
        # 노트북
        "notebooks/data_exploration",
        "notebooks/model_experiments",
        
        # 테스트
        "tests/data",
        "tests/models",
        
        # 로그 및 결과
        "logs",
        "results/predictions",
        "results/visualizations",
    ]
    
    print("📁 디렉토리 구조 생성 중...\n")
    
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")
    
    # .gitkeep 파일 생성 (빈 디렉토리도 Git에 포함되도록)
    gitkeep_dirs = [
        "data_samples/text",
        "data_samples/image",
        "docs/weekly_reports",
        "logs",
        "results",
    ]
    
    for directory in gitkeep_dirs:
        gitkeep_path = base_dir / directory / ".gitkeep"
        gitkeep_path.touch()
    
    print("\n✨ 디렉토리 구조 생성 완료!")
    print("\n📝 다음 단계:")
    print("1. 구글 드라이브의 이미지를 data/raw/image/ 폴더로 복사")
    print("2. python scripts/verify_data.py 로 데이터 확인")
    print("3. python src/data/preprocessing/preprocess_images.py 로 전처리 시작")

if __name__ == "__main__":
    create_directory_structure()
