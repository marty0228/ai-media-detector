import os
import sys
import torch
from PIL import Image
from io import BytesIO
import numpy as np

BASE_DIR = os.path.dirname(__file__)
TRUFOR_DIR = os.path.join(BASE_DIR, "trufor")

if TRUFOR_DIR not in sys.path:
    sys.path.insert(0, TRUFOR_DIR)

try:
    from config import _C as base_config
    from models.cmx.builder_np_conf import myEncoderDecoder as confcmx
except ImportError as e:
    print(f"Warning: Failed to import TruFor modules: {e}")

_model = None
_device = None


def build_trufor_config():
    """
    TruFor 기본 config를 clone한 뒤 trufor.yaml을 merge하여 반환합니다.
    BACKBONE 오류를 막기 위해 반드시 yaml 병합이 필요합니다.
    """
    cfg = base_config.clone()

    yaml_path = os.path.join(TRUFOR_DIR, "trufor.yaml")
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"TruFor config file not found: {yaml_path}")

    cfg.merge_from_file(yaml_path)
    cfg.freeze()
    return cfg


def find_weight_path():
    """
    우선순위:
    1) forensic_analysis/trufor/weights/trufor_genimage_best.pth.tar
    2) forensic_analysis/weights/trufor_genimage_best.pth.tar
    3) forensic_analysis/trufor/weights/trufor.pth.tar
    4) forensic_analysis/weights/trufor.pth.tar
    """
    candidates = [
        os.path.join(TRUFOR_DIR, "weights", "trufor_genimage_best.pth.tar"),
        os.path.join(BASE_DIR, "weights", "trufor_genimage_best.pth.tar"),
        os.path.join(TRUFOR_DIR, "weights", "trufor.pth.tar"),
        os.path.join(BASE_DIR, "weights", "trufor.pth.tar"),
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    return None


def load_model():
    """서버 기동 시 TruFor 모델의 아키텍처와 가중치를 메모리에 올립니다."""
    global _model, _device

    print("Loading Forensic Analysis (TruFor) Model...")

    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    weights_path = find_weight_path()
    if weights_path is None:
        print("-> WARNING: TruFor weight file not found.")
        print("-> Tried paths:")
        print(f"   - {os.path.join(TRUFOR_DIR, 'weights', 'trufor_genimage_best.pth.tar')}")
        print(f"   - {os.path.join(BASE_DIR, 'weights', 'trufor_genimage_best.pth.tar')}")
        print(f"   - {os.path.join(TRUFOR_DIR, 'weights', 'trufor.pth.tar')}")
        print(f"   - {os.path.join(BASE_DIR, 'weights', 'trufor.pth.tar')}")
        _model = None
        return

    try:
        cfg = build_trufor_config()

        _model = confcmx(cfg=cfg)

        checkpoint = torch.load(
            weights_path,
            map_location=_device,
            weights_only=False,
        )

        if "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]
        elif "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
        else:
            state_dict = checkpoint

        _model.load_state_dict(state_dict, strict=False)
        _model = _model.to(_device)
        _model.eval()

        print(f"-> TruFor weights loaded successfully from: {weights_path}")

    except Exception as e:
        print(f"-> Error initializing TruFor model: {e}")
        _model = None


def predict(image_bytes: bytes) -> dict:
    """Bytes 이미지를 TruFor 모델에 통과시켜 조작 확률(confidence)을 산출하여 반환합니다."""
    global _model, _device

    try:
        if _model is None:
            return {
                "model_name": "forensic_analysis",
                "predicted_idx": 1,
                "confidence": 0.5,
                "error": "TruFor weight file is missing or model failed to load."
            }

        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        img_np = np.array(image)

        img_tensor = torch.tensor(
            img_np.transpose(2, 0, 1),
            dtype=torch.float32
        ) / 256.0

        img_tensor = img_tensor.unsqueeze(0).to(_device)

        with torch.no_grad():
            pred, conf, det, npp = _model(img_tensor)

            if det is not None:
                det_prob = torch.sigmoid(det).item()
            else:
                det_prob = 0.5

            predicted_idx = 1 if det_prob >= 0.5 else 0

            return {
                "model_name": "forensic_analysis",
                "predicted_idx": predicted_idx,
                "confidence": round(det_prob, 4),
            }

    except Exception as e:
        print(f"Forensic Analysis prediction error: {e}")
        return {
            "model_name": "forensic_analysis",
            "predicted_idx": 0,
            "confidence": 0.5,
            "error": str(e)
        }