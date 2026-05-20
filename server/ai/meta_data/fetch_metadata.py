import os
import csv
import io
from typing import Any, Dict
from PIL import Image, ExifTags, ImageFile

# 손상되었거나 일부 잘린 이미지도 최대한 열 수 있도록 설정
ImageFile.LOAD_TRUNCATED_IMAGES = True


# ============================================================
# 0. 전역 상수 및 기본 설정
# ============================================================

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff")

# AI 생성 이미지에서 자주 발견되는 PNG text chunk key
AI_TEXT_KEYS = {
    "parameters",
    "prompt",
    "workflow",
    "description",
    "comment",
}

# AI 생성 도구나 생성 흔적으로 볼 수 있는 문자열
AI_VALUE_HINTS = {
    "stable diffusion",
    "midjourney",
    "dall-e",
    "dalle",
    "firefly",
    "novelai",
    "comfyui",
    "automatic1111",
    "invokeai",
    "c2pa",
    "ai generated",
    "generated",
    "gemini",
    "chatgpt",
    "openai",
}

# PIL의 EXIF tag id를 사람이 읽을 수 있는 이름으로 변환하기 위한 매핑
EXIF_TAGS = ExifTags.TAGS


# ============================================================
# 1. 범주형 메타데이터 정규화 함수
# ============================================================

def normalize_camera_brand(make: str, model: str) -> str:
    """
    카메라 제조사(make), 모델명(model)을 통합하여
    apple, samsung, canon, nikon 등 일반화된 카메라 브랜드로 변환한다.

    목적:
    - EXIF에 저장된 제조사/모델 문자열은 기기마다 형태가 다르므로 그대로 쓰기 어렵다.
    - 모델 학습에서는 원본 문자열보다 일반화된 camera_brand가 더 안정적이다.
    """

    text = f"{make} {model}".strip().lower()

    if not text:
        return "none"

    brand_rules = [
        "samsung",
        "apple",
        "canon",
        "nikon",
        "sony",
        "fujifilm",
        "xiaomi",
        "huawei",
        "google",
    ]

    for brand in brand_rules:
        if brand in text:
            return brand

        if brand == "samsung" and (text.startswith("sm-") or text.startswith("s9")):
            return "samsung"

        if brand == "apple" and "iphone" in text:
            return "apple"

        if brand == "fujifilm" and "fuji" in text:
            return "fujifilm"

        if brand == "google" and "pixel" in text:
            return "google"

    return "other"


def normalize_software_type(software: str) -> str:
    """
    EXIF Software 또는 PNG info에 남아 있는 software 문자열을
    camera_fw, editor, ai, unknown, none 중 하나로 정규화한다.

    목적:
    - Photoshop, Lightroom 등은 편집 도구로 분류
    - Stable Diffusion, Midjourney, DALL-E 등은 AI 도구로 분류
    - iPhone, Canon, Nikon 등은 카메라 펌웨어 계열로 분류
    """

    software = str(software).strip().lower()

    if not software or software in ["none", "nan", "null"]:
        return "none"

    editor_keywords = [
        "photoshop",
        "lightroom",
        "gimp",
        "snapseed",
        "picsart",
        "canva",
        "paint",
        "instagram",
    ]

    ai_keywords = [
        "stable diffusion",
        "midjourney",
        "dall-e",
        "dalle",
        "firefly",
        "novelai",
        "comfyui",
        "automatic1111",
        "invokeai",
        "leonardo",
        "gemini",
        "chatgpt",
        "openai",
    ]

    camera_keywords = [
        "iphone",
        "ios",
        "android",
        "samsung",
        "canon",
        "nikon",
        "sony",
        "camera",
    ]

    if any(keyword in software for keyword in editor_keywords):
        return "editor"

    if any(keyword in software for keyword in ai_keywords):
        return "ai"

    if software.startswith("sm-") or software.startswith("s9"):
        return "camera_fw"

    if any(keyword in software for keyword in camera_keywords):
        return "camera_fw"

    return "unknown"


# ============================================================
# 2. 메타데이터 추출 보조 함수
# ============================================================

def has_ai_prompt_like_text(info: Dict[str, Any]) -> bool:
    """
    PNG info, XMP, text chunk 안에 prompt나 AI 생성 도구 관련 문자열이 있는지 확인한다.
    """

    if not info:
        return False

    keys_text = " ".join(str(k).lower() for k in info.keys())
    values_text = " ".join(str(v).lower() for v in info.values())
    total_text = keys_text + " " + values_text

    return any(keyword in total_text for keyword in AI_VALUE_HINTS) or bool(AI_TEXT_KEYS & set(keys_text.split()))


def infer_source_type_from_path(image_path: str, label: int) -> str:
    """
    이미지 경로에서 세부 데이터 유형을 추출한다.

    예시:
    train_datasets/real/smartphone_original/a.jpg
    -> real_smartphone_original

    train_datasets/ai/ai_jpg_converted/a.jpg
    -> ai_ai_jpg_converted

    source_type은 이후 train/valid를 나눌 때 stratify 기준으로 사용된다.
    """

    norm_path = str(image_path).replace("\\", "/")
    parts = norm_path.split("/")

    label_name = "real" if label == 0 else "ai"

    if "train_datasets" in parts:
        idx = parts.index("train_datasets")
        after = parts[idx + 1:]

        if len(after) >= 2:
            class_folder = after[0]
            source_folder = after[1]

            if class_folder in ["real", "ai"]:
                return f"{class_folder}_{source_folder}"

    return f"{label_name}_unknown"


# ============================================================
# 3. 단일 이미지 메타데이터 추출 함수
# ============================================================

def extract_metadata(image_source, label: int = -1) -> Dict[str, Any]:
    """
    단일 이미지에서 메타데이터 feature를 추출한다.

    label:
    - real 이미지: 0
    - AI 이미지: 1
    - 예측용 단일 이미지: -1

    반환값:
    - RandomForest 모델 학습/예측에 사용할 feature dictionary
    """

    filename = os.path.basename(image_source) if isinstance(image_source, str) else "image_from_bytes"
    ext = os.path.splitext(filename)[1].lower()

    # ------------------------------------------------------------
    # 3.1 기본 feature 초기화
    # ------------------------------------------------------------

    res = dict.fromkeys(
        [
            "has_exif",
            "has_camera",
            "has_png_chunk",
            "has_prompt",
            "has_xmp",
            "has_make",
            "has_model",
            "has_datetime",
            "has_gps",
            "has_iso",
            "has_exposure_time",
            "has_fnumber",
            "has_focal_length",
            "has_orientation",
            "has_color_space",
            "file_size",
            "width",
            "height",
            "channels",
            "is_jpeg",
            "is_png",
            "is_webp",
            "metadata_empty",
            "exif_but_no_camera",
            "camera_but_no_datetime",
            "jpg_without_exif",
            "png_with_exif",
            "exif_field_count",
            "metadata_key_count",
            "is_screenshot_like",
        ],
        0,
    )

    res.update(
        {
            "aspect_ratio": 0.0,
            "mega_pixels": 0.0,
            "size_per_megapixel": 0.0,
            "make_raw": "None",
            "model_raw": "None",
            "camera_brand": "none",
            "software_raw": "None",
            "software_type": "none",
            "filename": filename,
            "filepath": str(image_source) if isinstance(image_source, str) else "",
            "label": label,
        }
    )

    try:
        # ------------------------------------------------------------
        # 3.2 파일 크기 추출
        # ------------------------------------------------------------

        if isinstance(image_source, str) and os.path.exists(image_source):
            res["file_size"] = os.path.getsize(image_source)

        source = io.BytesIO(image_source) if isinstance(image_source, bytes) else image_source

        with Image.open(source) as img:
            width, height = img.size
            image_format = (img.format or "").upper()

            # ------------------------------------------------------------
            # 3.3 이미지 기본 구조 feature
            # ------------------------------------------------------------

            res["width"] = int(width)
            res["height"] = int(height)
            res["aspect_ratio"] = round(width / height, 6) if height else 0.0

            res["is_jpeg"] = int(image_format in ["JPEG", "JPG"] or ext in [".jpg", ".jpeg"])
            res["is_png"] = int(image_format == "PNG" or ext == ".png")
            res["is_webp"] = int(image_format == "WEBP" or ext == ".webp")

            mega_pixels = (width * height) / 1_000_000
            res["mega_pixels"] = round(mega_pixels, 6)

            if mega_pixels > 0:
                res["size_per_megapixel"] = round(res["file_size"] / mega_pixels, 6)

            mode_to_channels = {
                "1": 1,
                "L": 1,
                "P": 1,
                "RGB": 3,
                "RGBA": 4,
                "CMYK": 4,
                "YCbCr": 3,
                "LAB": 3,
                "HSV": 3,
                "I": 1,
                "F": 1,
            }

            res["channels"] = mode_to_channels.get(img.mode, len(img.getbands()))

            # ------------------------------------------------------------
            # 3.4 EXIF 메타데이터 추출
            # ------------------------------------------------------------

            exif = img.getexif()

            if exif:
                res["has_exif"] = 1
                res["exif_field_count"] = len(exif)

                for tag_id, value in exif.items():
                    tag_name = EXIF_TAGS.get(tag_id, tag_id)

                    if tag_name == "Make":
                        res["has_make"] = 1
                        res["make_raw"] = str(value).strip()

                    elif tag_name == "Model":
                        res["has_model"] = 1
                        res["model_raw"] = str(value).strip()

                    elif tag_name in ["DateTime", "DateTimeOriginal", "DateTimeDigitized"]:
                        res["has_datetime"] = 1

                    elif tag_name == "Software":
                        res["software_raw"] = str(value).strip()

                    elif tag_name in ["ISOSpeedRatings", "PhotographicSensitivity"]:
                        res["has_iso"] = 1

                    elif tag_name == "ExposureTime":
                        res["has_exposure_time"] = 1

                    elif tag_name == "FNumber":
                        res["has_fnumber"] = 1

                    elif tag_name == "FocalLength":
                        res["has_focal_length"] = 1

                    elif tag_name == "Orientation":
                        res["has_orientation"] = 1

                    elif tag_name == "ColorSpace":
                        res["has_color_space"] = 1

                    elif tag_name == "GPSInfo" and value:
                        res["has_gps"] = 1

                res["has_camera"] = int(res["has_make"] or res["has_model"])

            res["metadata_key_count"] += res["exif_field_count"]

            # ------------------------------------------------------------
            # 3.5 PNG/WEBP text chunk 및 info 추출
            # ------------------------------------------------------------

            info = img.info or {}
            info_keys = {str(k).lower() for k in info.keys()}

            res["metadata_key_count"] += len(info_keys)

            if AI_TEXT_KEYS & info_keys:
                res["has_png_chunk"] = 1
                res["has_prompt"] = 1

            for key, value in info.items():
                key_lower = str(key).lower()
                value_text = str(value).strip()

                if key_lower in AI_TEXT_KEYS or (key_lower == "software" and value_text):
                    res["has_png_chunk"] = 1

                    if key_lower == "software":
                        res["software_raw"] = value_text

                    if key_lower in AI_TEXT_KEYS and value_text:
                        res["has_prompt"] = 1

                if value_text and any(hint in value_text.lower() for hint in AI_VALUE_HINTS):
                    res["has_png_chunk"] = 1
                    res["has_prompt"] = 1

            # ------------------------------------------------------------
            # 3.6 XMP 메타데이터 추출
            # ------------------------------------------------------------

            if hasattr(img, "getxmp"):
                try:
                    xmp = img.getxmp()
                except Exception:
                    xmp = None

                if xmp:
                    res["has_xmp"] = 1

                    if isinstance(xmp, dict):
                        res["metadata_key_count"] += len(xmp.keys())
                    else:
                        res["metadata_key_count"] += 1

                    xmp_text = str(xmp).lower()

                    for tool in [
                        "midjourney",
                        "dall-e",
                        "dalle",
                        "firefly",
                        "novelai",
                        "stable diffusion",
                        "comfyui",
                        "gemini",
                        "chatgpt",
                    ]:
                        if tool in xmp_text:
                            res["software_raw"] = tool.title()
                            break

                    if any(hint in xmp_text for hint in AI_VALUE_HINTS):
                        res["has_prompt"] = 1

        # ------------------------------------------------------------
        # 3.7 파생 feature 생성
        # ------------------------------------------------------------

        res["camera_brand"] = normalize_camera_brand(res["make_raw"], res["model_raw"])
        res["software_type"] = normalize_software_type(res["software_raw"])

        res["metadata_empty"] = int(
            not any(
                [
                    res["has_exif"],
                    res["has_xmp"],
                    res["has_prompt"],
                    res["has_png_chunk"],
                    res["has_make"],
                    res["has_model"],
                    res["has_datetime"],
                    res["has_gps"],
                    res["has_iso"],
                    res["has_exposure_time"],
                ]
            )
        )

        res["exif_but_no_camera"] = int(res["has_exif"] and not res["has_camera"])
        res["camera_but_no_datetime"] = int(res["has_camera"] and not res["has_datetime"])
        res["jpg_without_exif"] = int(res["is_jpeg"] and not res["has_exif"])
        res["png_with_exif"] = int(res["is_png"] and res["has_exif"])

        # 실제 스크린샷은 PNG이면서 EXIF, 카메라 정보, 촬영 시간이 없는 경우가 많다.
        res["is_screenshot_like"] = int(
            res["is_png"]
            and not res["has_exif"]
            and not res["has_camera"]
            and not res["has_datetime"]
        )

    except Exception as e:
        print(f"[WARN] {filename}: {e}")

    return res


# ============================================================
# 4. 폴더 단위 이미지 수집 함수
# ============================================================

def collect_images_from_folder(folder_path, label: int):
    """
    지정된 폴더 아래의 모든 이미지 파일을 재귀적으로 탐색하여
    메타데이터 feature row 목록을 생성한다.

    하위 폴더 구조:
    train_datasets/real/smartphone_original/...
    train_datasets/ai/stable_diffusion/...
    """

    rows = []

    if not os.path.exists(folder_path):
        print(f"[경고] 폴더 없음: {folder_path}")
        return rows

    print(f"\n[이미지 수집 시작] folder_path={folder_path}, label={label}")

    total_file_count = 0
    image_file_count = 0
    error_count = 0

    for root, _, files in os.walk(folder_path):
        for file in files:
            total_file_count += 1

            ext = os.path.splitext(file)[1].lower()

            if ext not in IMAGE_EXTENSIONS:
                continue

            image_file_count += 1
            image_path = os.path.join(root, file)

            try:
                metadata = extract_metadata(image_path, label=label)
                metadata["filename"] = file
                metadata["filepath"] = image_path
                metadata["label"] = label
                metadata["source_type"] = infer_source_type_from_path(image_path, label)

                rows.append(metadata)

            except Exception as e:
                error_count += 1
                print(f"[오류] {image_path} 처리 실패: {e}")

    print(f"[이미지 수집 완료] {folder_path}")
    print(f"- 전체 파일 수: {total_file_count}")
    print(f"- 이미지 파일 수: {image_file_count}")
    print(f"- 정상 처리 수: {len(rows)}")
    print(f"- 오류 수: {error_count}")

    return rows


# ============================================================
# 5. CSV 저장 함수
# ============================================================

def save_to_csv(rows, output_file="metadata_dataset.csv"):
    """
    추출한 메타데이터 row 목록을 CSV로 저장한다.
    """

    if not rows:
        print("[경고] 저장할 row가 없습니다.")
        return None

    fieldnames = [
        "filename",
        "filepath",
        "source_type",
        "label",

        "has_exif",
        "has_camera",
        "has_png_chunk",
        "has_prompt",
        "has_xmp",
        "has_make",
        "has_model",
        "has_datetime",
        "has_gps",
        "has_iso",
        "has_exposure_time",
        "has_fnumber",
        "has_focal_length",
        "has_orientation",
        "has_color_space",

        "make_raw",
        "model_raw",
        "camera_brand",
        "software_raw",
        "software_type",

        "file_size",
        "width",
        "height",
        "aspect_ratio",
        "channels",
        "is_jpeg",
        "is_png",
        "is_webp",
        "mega_pixels",
        "size_per_megapixel",

        "metadata_empty",
        "exif_but_no_camera",
        "camera_but_no_datetime",
        "jpg_without_exif",
        "png_with_exif",

        "exif_field_count",
        "metadata_key_count",
        "is_screenshot_like",
    ]

    with open(output_file, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"저장 완료: {output_file} ({len(rows)}개)")
    return output_file


# ============================================================
# 6. 단독 실행 시 전체 데이터셋 CSV 생성
# ============================================================

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(base_dir, "train_datasets")

    real_dir = os.path.join(dataset_dir, "real")
    ai_dir = os.path.join(dataset_dir, "ai")

    rows = []
    rows += collect_images_from_folder(real_dir, 0)
    rows += collect_images_from_folder(ai_dir, 1)

    model_dir = os.path.join(base_dir, "model")
    os.makedirs(model_dir, exist_ok=True)

    output_path = os.path.join(model_dir, "metadata_dataset_expanded.csv")
    save_to_csv(rows, output_path)