"""
프로젝트 디렉토리 구조를 자동으로 생성하는 스크립트
최초 1회 실행
"""
import os
from pathlib import Path

def create_directory_structure():
    base_dir = Path(__file__).parent.parent
    
    directories = [
        # 데이터 디렉토리 (Git에서 제외)
        "data/raw/text/ai_generated",
        "data/raw/text/human_written",
        "data/raw/image/ai_generated",
        "data/raw/image/real",
        "data/processed",
        "data/splits",
        
        # 샘플 데이터 (Git에 포함)
        "data_samples/text",
        "data_samples/image/ai_sample_10",
        "data_samples/image/real_sample_10",
        
        # 모델 디렉토리
        "models/text",
        "models/image",
        
        # 소스 코드
        "src/data/collectors",
        "src/data/preprocessing",
        "src/models/text",
        "src/models/image",
        "src/api",
        "src/web",
        
        # 문서
        "docs/weekly_reports",
        
        # 노트북
        "notebooks/experiments",
        
        # 테스트
        "tests/data",
        "tests/models",
        
        # 로그
        "logs",
    ]
    
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")
    
    # .gitkeep 파일 생성 (빈 디렉토리도 Git에 포함)
    gitkeep_dirs = [
        "data_samples/text",
        "data_samples/image",
        "docs/weekly_reports",
        "logs",
    ]
    
    for directory in gitkeep_dirs:
        gitkeep_path = base_dir / directory / ".gitkeep"
        gitkeep_path.touch()
    
    print("\n✨ 디렉토리 구조 생성 완료!")
    print("\n📝 다음 단계:")
    print("1. docs/data_sources.md에서 데이터 출처 확인")
    print("2. 팀 공유 드라이브에서 데이터 다운로드")
    print("3. python scripts/download_data.py 실행 (선택)")

if __name__ == "__main__":
    create_directory_structure()
