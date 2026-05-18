import os
import sys
sys.path.append(os.getcwd())
try:
    from server.ai.water_mark.predict import load_model, predict_watermark
    load_model()
    dataset = "server/ai/water_mark/datasets/gemini"
    files = ["Gemini_Generated_Image_rjnp0srjnp (1).png", "Gemini_Generated_Image_rjnp0srjnp (2).png", "Gemini_Generated_Image_rjnp0srjnp (3).png"]
    for f in files:
        path = os.path.join(dataset, f)
        res = predict_watermark(path)
        print(f"File: {f}")
        print(f"predicted_idx: {res.get('predicted_idx')}")
        print(f"confidence: {res.get('confidence')}")
        print(f"threshold: {res.get('threshold')}")
        conf = res.get('confidence', 0)
        if 0.12 <= conf <= 0.13:
            status = "Positive" if res.get('predicted_idx') == 1 else "Negative"
            print(f"NOTE: Image with confidence {conf} is now classified as {status}")
        print("-" * 20)
except Exception as e:
    print(f"Error: {e}")
