import os
import io
import sys
from PIL import Image

# Ensure project root is in path
sys.path.append(os.getcwd())

from server.ai.water_mark.predict import load_model, predict

load_model()
dataset_dir = 'server/ai/water_mark/datasets/gemini'
if not os.path.exists(dataset_dir):
    print(f'Dataset directory not found: {dataset_dir}')
    sys.exit(1)

files = [f for f in os.listdir(dataset_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:3]

for filename in files:
    img_path = os.path.join(dataset_dir, filename)
    with open(img_path, 'rb') as f:
        img_bytes = f.read()
    
    res = predict(img_bytes)
    
    print(f"File: {filename}")
    print(f"  predicted_idx: {res.get('predicted_idx')}")
    print(f"  confidence: {res.get('confidence')}")
    
    details = res.get('details', {})
    boxes = details.get('boxes', [])[:2]
    for i, box in enumerate(boxes):
        # Clean up box output to match requested format
        print(f"  Box {i+1}: {box}")
    
    threshold = res.get('threshold', 0.5)
    if res.get('confidence', 0) >= threshold:
        print(f"  Status: Crossed threshold ({threshold})")
    else:
        print(f"  Status: Below threshold ({threshold})")
