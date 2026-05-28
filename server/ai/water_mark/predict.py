import os
import io
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

model = None
weights_path = None
prediction_threshold = float(os.getenv("WATERMARK_THRESHOLD", "0.5"))
# 기본 결정 임계값을 너무 낮게 잡으면 작은 출력도 유효로 처리됩니다. 빠른 수정으로 기본값을 상향합니다.
decision_threshold = float(os.getenv("WATERMARK_DECISION_THRESHOLD", "0.15"))
roi_fraction = float(os.getenv("WATERMARK_ROI_FRACTION", "0.45"))
roi_resize = float(os.getenv("WATERMARK_ROI_RESIZE", "1.5"))
roi_fractions = [float(v) for v in os.getenv("WATERMARK_ROI_FRACTIONS", "0.65,0.45,0.30").split(",") if v.strip()]
roi_resizes = [float(v) for v in os.getenv("WATERMARK_ROI_RESIZES", "2.0,1.5,1.0").split(",") if v.strip()]
corner_fractions = [float(v) for v in os.getenv("WATERMARK_CORNER_FRACTIONS", "0.15,0.12,0.10").split(",") if v.strip()]
corner_resizes = [float(v) for v in os.getenv("WATERMARK_CORNER_RESIZES", "8.0,7.0,6.0").split(",") if v.strip()]
# 코너 박스 보정 파라미터(환경변수로 조정 가능)
corner_base = float(os.getenv("WATERMARK_CORNER_BASE", "0.75"))
corner_multiplier = float(os.getenv("WATERMARK_CORNER_MULTIPLIER", "0.2"))
corner_max = float(os.getenv("WATERMARK_CORNER_MAX", "0.95"))

BASE_PATH = Path(__file__).resolve().parent
PRIMARY_WEIGHTS = BASE_PATH / "runs" / "detect" / "finetune_gemini_v1" / "weights" / "best.pt"
FALLBACK_WEIGHTS = BASE_PATH / "runs" / "detect" / "watermark_model" / "final_v1" / "weights" / "best.pt"

# ---------------------------------------------------------
# 1. 모델 초기화 및 로드
# ---------------------------------------------------------
def load_model():
    global model, weights_path
    print("Loading Watermark AI model...")

    if not YOLO:
        print("Warning: ultralytics is not installed.")
        return

    for candidate in (PRIMARY_WEIGHTS, FALLBACK_WEIGHTS):
        if candidate.exists():
            model = YOLO(str(candidate))
            weights_path = candidate
            print(f"Watermark model loaded successfully from: {candidate}")
            return

    print(
        "Warning: Watermark model files not found. "
        f"Checked: {PRIMARY_WEIGHTS} and {FALLBACK_WEIGHTS}"
    )


def _collect_results(results, x_offset: float = 0.0, y_offset: float = 0.0) -> tuple[float, list]:
    max_conf = 0.0
    boxes = []

    for r in results:
        if len(r.boxes) == 0:
            continue

        result_max = float(r.boxes.conf.max())
        max_conf = max(max_conf, result_max)

        for box, conf in zip(r.boxes.xyxy.tolist(), r.boxes.conf.tolist()):
            boxes.append({
                "xyxy": [
                    round(float(box[0] + x_offset), 2),
                    round(float(box[1] + y_offset), 2),
                    round(float(box[2] + x_offset), 2),
                    round(float(box[3] + y_offset), 2),
                ],
                "confidence": round(float(conf), 4),
            })

    return max_conf, boxes


def _prep_roi(image: Image.Image) -> Image.Image:
    image = ImageOps.autocontrast(image)
    image = ImageEnhance.Sharpness(image).enhance(1.4)
    image = ImageEnhance.Contrast(image).enhance(1.15)
    return image


def _is_corner_watermark_candidate(box: dict, image_width: int, image_height: int) -> bool:
    x1, y1, x2, y2 = box["xyxy"]
    box_width = max(0.0, x2 - x1)
    box_height = max(0.0, y2 - y1)
    box_area = box_width * box_height
    image_area = float(image_width * image_height) if image_width and image_height else 1.0
    center_x = x1 + (box_width / 2.0)
    center_y = y1 + (box_height / 2.0)

    return (
        box.get("pass", "").startswith("corner_")
        and center_x >= image_width * 0.55
        and center_y >= image_height * 0.55
        and box_area <= image_area * 0.12
    )

# ---------------------------------------------------------
# 2. 이미지 바이트 기반 워터마크 예측 실행
# ---------------------------------------------------------
def predict(image_bytes: bytes) -> dict:
    global model, weights_path
    
    # 모델 로드 실패 시 더미 데이터 반환
    if not model:
        return {
            "model_name": "Water Mark",
            "predicted_idx": 0,
            "confidence": 0.0
        }
    
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        width, height = image.size

        search_passes = [("full", image, 0, 0)]

        for fraction in roi_fractions:
            roi_left = int(width * (1.0 - fraction))
            roi_top = int(height * (1.0 - fraction))
            roi = image.crop((roi_left, roi_top, width, height))

            resize_factor = roi_resize if fraction == roi_fraction else roi_resizes[min(len(roi_resizes) - 1, roi_fractions.index(fraction))] if roi_resizes else 1.0
            if resize_factor > 1.0 and roi.size[0] > 0 and roi.size[1] > 0:
                roi = roi.resize(
                    (max(1, int(roi.size[0] * resize_factor)), max(1, int(roi.size[1] * resize_factor))),
                    Image.Resampling.BILINEAR,
                )

            search_passes.append((f"roi_{fraction:.2f}", roi, roi_left, roi_top))

        for index, fraction in enumerate(corner_fractions):
            corner_left = int(width * (1.0 - fraction))
            corner_top = int(height * (1.0 - fraction))
            corner = image.crop((corner_left, corner_top, width, height))

            resize_factor = corner_resizes[min(index, len(corner_resizes) - 1)] if corner_resizes else 1.0
            if resize_factor > 1.0 and corner.size[0] > 0 and corner.size[1] > 0:
                corner = corner.resize(
                    (max(1, int(corner.size[0] * resize_factor)), max(1, int(corner.size[1] * resize_factor))),
                    Image.Resampling.BILINEAR,
                )

            search_passes.append((f"corner_{fraction:.2f}", corner, corner_left, corner_top))

        max_conf = 0.0
        boxes = []
        for pass_name, pass_image, x_offset, y_offset in search_passes:
            pass_results = model(_prep_roi(pass_image), conf=0.005, verbose=False)
            pass_max_conf, pass_boxes = _collect_results(pass_results, x_offset=x_offset, y_offset=y_offset)

            if pass_max_conf > max_conf:
                max_conf = pass_max_conf

            for box in pass_boxes:
                box["pass"] = pass_name
            boxes.extend(pass_boxes)

        boxes.sort(key=lambda item: item["confidence"], reverse=True)

        best_corner_box = next(
            (box for box in boxes if _is_corner_watermark_candidate(box, width, height)),
            None,
        )
        best_corner_conf = float(best_corner_box["confidence"]) if best_corner_box else 0.0

        if best_corner_box:
            # 코너 박스 보정을 덜 공격적으로 적용: 기본값(base) + 작은 멀티플러
            calibrated_confidence = max(corner_base, min(corner_max, corner_base + (best_corner_conf * corner_multiplier)))
            predicted_idx = 1
            confidence_mode = "corner-calibrated"
        elif max_conf >= decision_threshold:
            calibrated_confidence = max(0.70, min(0.89, 0.70 + (max_conf * 2.0)))
            predicted_idx = 1
            confidence_mode = "model-calibrated"
        else:
            calibrated_confidence = max(0.0, min(0.69, max_conf))
            predicted_idx = 0
            confidence_mode = "raw"
                
        return {
            "model_name": "Water Mark",
            "predicted_idx": predicted_idx,
            "confidence": calibrated_confidence,
            "raw_confidence": max_conf
            ,"threshold": decision_threshold,
            "model_threshold": prediction_threshold,
            "weights_path": str(weights_path) if weights_path else None,
            "details": {
                "boxes": boxes,
                "calibration": {
                    "mode": confidence_mode,
                    "corner_box_found": bool(best_corner_box),
                    "corner_box_confidence": best_corner_conf,
                },
                "roi": {
                    "enabled": True,
                    "decision_threshold": decision_threshold,
                    "fraction": roi_fraction,
                    "resize": roi_resize,
                    "fractions": roi_fractions,
                    "resizes": roi_resizes,
                    "corner_fractions": corner_fractions,
                    "corner_resizes": corner_resizes,
                },
            }
        }
        
    except Exception as e:
        print(f"Error in watermark prediction: {e}")
        return {
            "model_name": "Water Mark",
            "predicted_idx": 0,
            "confidence": 0.0
            ,"threshold": decision_threshold,
            "model_threshold": prediction_threshold,
            "weights_path": str(weights_path) if weights_path else None,
            "details": {"error": str(e)}
        }

if __name__ == "__main__":
    load_model()