"""
데이터 디렉토리를 검증하고 통계를 출력하는 스크립트
실행: python scripts/verify_data.py
"""
import os
from pathlib import Path
from collections import defaultdict

def verify_data_structure():
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data" / "raw"
    
    print("🔍 데이터 검증 시작...\n")
    
    # 이미지 데이터 확인
    image_stats = defaultdict(int)
    image_formats = defaultdict(int)
    
    image_dirs = {
        "AI 생성 이미지": data_dir / "image" / "ai_generated",
        "실제 이미지": data_dir / "image" / "real"
    }
    
    for label, path in image_dirs.items():
        if path.exists():
            files = list(path.glob("*"))
            image_files = [f for f in files if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']]
            image_stats[label] = len(image_files)
            
            for img in image_files:
                image_formats[img.suffix.lower()] += 1
            
            print(f"✅ {label}: {len(image_files)}개")
        else:
            print(f"⚠️  {label}: 폴더가 없습니다 - {path}")
    
    # 텍스트 데이터 확인
    text_stats = defaultdict(int)
    
    text_dirs = {
        "AI 생성 텍스트": data_dir / "text" / "ai_generated",
        "인간 작성 텍스트": data_dir / "text" / "human_written"
    }
    
    for label, path in text_dirs.items():
        if path.exists():
            files = list(path.glob("*.json")) + list(path.glob("*.txt")) + list(path.glob("*.csv"))
            text_stats[label] = len(files)
            print(f"✅ {label}: {len(files)}개 파일")
        else:
            print(f"⚠️  {label}: 폴더가 없습니다 - {path}")
    
    # 통계 요약
    print("\n" + "="*50)
    print("📊 데이터 통계 요약")
    print("="*50)
    
    total_images = sum(image_stats.values())
    print(f"\n이미지 전체: {total_images}개")
    for label, count in image_stats.items():
        percentage = (count / total_images * 100) if total_images > 0 else 0
        print(f"  - {label}: {count}개 ({percentage:.1f}%)")
    
    if image_formats:
        print(f"\n이미지 포맷 분포:")
        for fmt, count in image_formats.items():
            print(f"  - {fmt}: {count}개")
    
    print(f"\n텍스트 파일 전체: {sum(text_stats.values())}개")
    for label, count in text_stats.items():
        print(f"  - {label}: {count}개")
    
    # 권장사항
    print("\n" + "="*50)
    print("💡 권장사항")
    print("="*50)
    
    if total_images < 1000:
        print("⚠️  이미지가 1000개 미만입니다. 추가 수집을 권장합니다.")
    
    if image_stats.get("AI 생성 이미지", 0) != image_stats.get("실제 이미지", 0):
        print("⚠️  AI 이미지와 실제 이미지 개수가 불균형합니다.")
        print(f"   균형을 맞추려면: {abs(image_stats.get('AI 생성 이미지', 0) - image_stats.get('실제 이미지', 0))}개 더 필요")
    
    if total_images > 0:
        print("✅ 데이터 검증 완료! 다음 단계: 전처리 실행")
    else:
        print("❌ 데이터가 없습니다. 구글 드라이브에서 data/raw/ 폴더로 복사하세요.")

if __name__ == "__main__":
    verify_data_structure()
