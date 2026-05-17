import shutil
from pathlib import Path

src = Path('runs/detect/train/weights/best.pt')
dst = Path('server/ai/water_mark/runs/detect/finetune_gemini_v1/weights/best.pt')

if src.exists():
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f'✓ Model copied to: {dst}')
    print(f'  Size: {dst.stat().st_size / 1e6:.1f} MB')
else:
    print(f'✗ Source not found: {src}')
