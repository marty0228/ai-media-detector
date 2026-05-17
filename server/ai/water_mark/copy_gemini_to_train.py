import shutil
from pathlib import Path

gemini_img = Path('server/ai/water_mark/datasets/gemini')
gemini_lbl = gemini_img / 'labels'
train_img = Path('server/ai/water_mark/datasets/train/images')
train_lbl = Path('server/ai/water_mark/datasets/train/labels')

# Copy Gemini images and labels to train
for img in gemini_img.glob('*.png'):
    dst = train_img / img.name
    shutil.copy2(img, dst)
    print(f'Copied {img.name}')

for lbl in gemini_lbl.glob('*.txt'):
    dst = train_lbl / lbl.name
    shutil.copy2(lbl, dst)
    print(f'Copied label {lbl.name}')

print(f'Train images: {len(list(train_img.glob("*")))}')
print(f'Train labels: {len(list(train_lbl.glob("*")))}')
