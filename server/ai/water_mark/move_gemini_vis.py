import os, shutil, sys

src = r"C:\Users\dhlee\OneDrive\바탕 화면\ai-media-detector\runs\detect\server\ai\water_mark\runs\detect\gemini_vis"
dst = r"C:\Users\dhlee\OneDrive\바탕 화면\ai-media-detector\server\ai\water_mark\runs\detect\gemini_vis"

if not os.path.exists(src):
    print("SRC_NOT_FOUND")
    sys.exit(1)

if os.path.exists(dst):
    shutil.rmtree(dst)

os.makedirs(os.path.dirname(dst), exist_ok=True)
shutil.move(src, dst)
print("MOVED_OK")
