"""
Re-test Gemini images with fine-tuned model (post-Gemini watermark training)
Compare before/after detection confidence
"""
import sys
from pathlib import Path
from PIL import Image
from io import BytesIO
import json

# Add server to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ultralytics import YOLO

def test_gemini_images(model_path, img_dir, thresholds="0.05,0.10,0.30"):
    """Test all images in gemini folder and report statistics."""
    
    model = YOLO(model_path)
    
    img_dir = Path(img_dir)
    images = sorted(img_dir.glob("*.png"))
    
    if not images:
        print(f"No images found in {img_dir}")
        return
    
    print(f"\n{'='*70}")
    print(f"Testing {len(images)} Gemini images with: {model_path}")
    print(f"{'='*70}\n")
    
    results = []
    
    for img_path in images:
        try:
            # Read image
            img = Image.open(img_path)
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Predict
            pred = model.predict(source=img_path, conf=0.01, verbose=False)
            
            # Extract max confidence
            max_conf = 0.0
            if pred and len(pred) > 0:
                boxes = pred[0].boxes
                if len(boxes) > 0:
                    max_conf = float(boxes.conf.max())
            
            results.append((img_path.name, max_conf))
            print(f"{img_path.name:50} → {max_conf:.4f}")
        
        except Exception as e:
            print(f"{img_path.name:50} → ERROR: {e}")
    
    # Statistics
    print(f"\n{'='*70}\nStatistics:\n")
    confs = [c for _, c in results]
    print(f"Mean confidence: {sum(confs)/len(confs):.4f}")
    print(f"Max confidence:  {max(confs):.4f}")
    print(f"Min confidence:  {min(confs):.4f}")
    
    # Threshold analysis
    threshold_list = [float(t) for t in thresholds.split(',')]
    print(f"\nThreshold Analysis:")
    for thresh in threshold_list:
        positives = sum(1 for _, c in results if c >= thresh)
        print(f"  Threshold {thresh:.2f} → Positives: {positives}/{len(results)}")
    
    print(f"\n{'='*70}\n")
    
    # Top 5 detections
    top5 = sorted(results, key=lambda x: x[1], reverse=True)[:5]
    print("Top 5 Detections:")
    for i, (name, conf) in enumerate(top5, 1):
        print(f"  {i}. {name:50} → {conf:.4f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {Path(__file__).name} <image_dir> [--thresholds 0.05,0.10,0.30]")
        sys.exit(1)
    
    img_dir = sys.argv[1]
    thresholds = "0.05,0.10,0.30"
    
    if len(sys.argv) > 3 and sys.argv[2] == "--thresholds":
        thresholds = sys.argv[3]
    
    model_path = "server/ai/water_mark/runs/detect/finetune_gemini_v1/weights/best.pt"
    test_gemini_images(model_path, img_dir, thresholds)
