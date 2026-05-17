"""
Auto-detect Gemini watermarks (bottom-right) and generate YOLO labels.
Gemini always places its watermark at bottom-right, so we:
1. Detect edges/features in bottom-right region
2. Find contours (watermark bbox)
3. Generate normalized YOLO label
"""

import os
import cv2
import numpy as np
from pathlib import Path

# Paths
GEMINI_IMG_DIR = Path("server/ai/water_mark/datasets/gemini")
GEMINI_LABEL_DIR = GEMINI_IMG_DIR / "labels"
GEMINI_LABEL_DIR.mkdir(exist_ok=True)

def detect_watermark_bbox(img_path):
    """
    Auto-detect watermark in bottom-right region.
    Returns (cx, cy, w, h) normalized coords, or None if not detected.
    """
    img = cv2.imread(str(img_path))
    if img is None:
        return None
    
    h, w = img.shape[:2]
    
    # Crop bottom-right region (last 30% x 30%)
    y_start = int(h * 0.7)
    x_start = int(w * 0.7)
    roi = img[y_start:, x_start:]
    
    # Convert to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Apply Canny edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        # Fallback: assume fixed bottom-right position
        # Gemini logo typically ~8-12% of image, at bottom-right
        cx_norm = 0.94  # 94% right
        cy_norm = 0.94  # 94% down
        w_norm = 0.10   # 10% width
        h_norm = 0.10   # 10% height
        return (cx_norm, cy_norm, w_norm, h_norm)
    
    # Find largest contour (likely the watermark)
    largest = max(contours, key=cv2.contourArea)
    x, y, bw, bh = cv2.boundingRect(largest)
    
    # Convert to image coords (accounting for ROI offset)
    x_img = x_start + x
    y_img = y_start + y
    
    # Normalize to [0, 1]
    cx_norm = (x_img + bw / 2) / w
    cy_norm = (y_img + bh / 2) / h
    w_norm = bw / w
    h_norm = bh / h
    
    # Clamp to valid range
    cx_norm = max(0, min(1, cx_norm))
    cy_norm = max(0, min(1, cy_norm))
    w_norm = max(0.01, min(1, w_norm))
    h_norm = max(0.01, min(1, h_norm))
    
    return (cx_norm, cy_norm, w_norm, h_norm)

def main():
    # Find all PNG/JPG images in gemini folder
    img_extensions = ['.png', '.jpg', '.jpeg']
    image_files = []
    for ext in img_extensions:
        image_files.extend(GEMINI_IMG_DIR.glob(f"*{ext}"))
        image_files.extend(GEMINI_IMG_DIR.glob(f"*{ext.upper()}"))
    
    image_files = sorted(set(image_files))  # Remove duplicates
    
    print(f"Found {len(image_files)} images")
    
    for img_path in image_files:
        # Detect watermark
        bbox = detect_watermark_bbox(img_path)
        if bbox is None:
            print(f"SKIP {img_path.name} (no image)")
            continue
        
        # Create label file
        label_path = GEMINI_LABEL_DIR / (img_path.stem + ".txt")
        cx, cy, bw, bh = bbox
        
        # YOLO format: class cx cy w h (class=0 for watermark)
        with open(label_path, "w") as f:
            f.write(f"0 {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}\n")
        
        print(f"OK {img_path.name} → bbox=({cx:.3f}, {cy:.3f}, {bw:.3f}, {bh:.3f})")
    
    print(f"\nGenerated {len(list(GEMINI_LABEL_DIR.glob('*.txt')))} label files")

if __name__ == "__main__":
    main()
