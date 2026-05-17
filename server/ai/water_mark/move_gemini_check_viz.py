import shutil
from pathlib import Path

src = Path(r"C:\Users\dhlee\OneDrive\바탕 화면\ai-media-detector\runs\detect\server\ai\water_mark\runs\detect\gemini_check_viz")
dst = Path(r"C:\Users\dhlee\OneDrive\바탕 화면\ai-media-detector\server\ai\water_mark\runs\detect\gemini_check_viz")

if not src.exists():
    print(f"SRC_NOT_FOUND: {src}")
    raise SystemExit(1)

if dst.exists():
    shutil.rmtree(dst)

dst.parent.mkdir(parents=True, exist_ok=True)
shutil.move(str(src), str(dst))
print(f"MOVED_OK: {dst}")
