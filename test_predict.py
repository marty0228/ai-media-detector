import os
import sys

# Add the root directory to sys.path to ensure imports work
sys.path.append(os.getcwd())

from server.ai.water_mark.predict import load_model, predict

def test_sample():
    load_model()
    image_path = r"server\ai\water_mark\datasets\gemini\Gemini_Generated_Image_rjnp0srjnp0srjnp (1).png"
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        
    results = predict(image_bytes)
    
    predicted_idx = results.get('predicted_idx')
    confidence = results.get('confidence')
    threshold = results.get('threshold')
    details = results.get('details', {})
    boxes = details.get('boxes', [])
    
    print(f"predicted_idx: {predicted_idx}")
    print(f"confidence: {confidence}")
    print(f"threshold: {threshold}")
    
    top_3 = boxes[:3]
    for i, box in enumerate(top_3):
        print(f"Box {i+1}: Pass={box.get('pass')}, Score={box.get('confidence')}, Box={box.get('xyxy')}")
        
    if top_3:
        is_corner = "Yes" if str(top_3[0].get('pass', '')).startswith('corner_') else "No"
        print(f"Top box from corner pass: {is_corner}")

if __name__ == '__main__':
    test_sample()
