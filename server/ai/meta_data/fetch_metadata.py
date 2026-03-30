import os
import csv
import io
import math
from typing import Any, Dict

import numpy as np
import cv2
from PIL import Image, ExifTags

# 처리할 이미지 확장자
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp')

# PNG 텍스트 청크 / 메타데이터에서 확인할 키워드
AI_TEXT_KEYS = {'parameters', 'prompt', 'workflow', 'description', 'comment'}
AI_VALUE_HINTS = {
    'stable diffusion', 'midjourney', 'dall-e', 'dalle', 'firefly',
    'novelai', 'comfyui', 'automatic1111', 'invokeai', 'c2pa',
    'ai generated', 'generated'
}

# EXIF 태그 이름 매핑
EXIF_TAGS = ExifTags.TAGS
GPS_TAGS = ExifTags.GPSTAGS


def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def rational_to_float(value):
    """EXIF의 IFDRational / tuple 등을 float로 안전 변환"""
    try:
        if value is None:
            return 0.0
        if isinstance(value, tuple) and len(value) == 2:
            num, den = value
            if den == 0:
                return 0.0
            return float(num) / float(den)
        return float(value)
    except Exception:
        return 0.0


def normalize_camera_brand(make: str, model: str) -> str:
    text = f"{make} {model}".strip().lower()

    if not text:
        return 'none'
    if 'samsung' in text or text.startswith('sm-') or text.startswith('s9'):
        return 'samsung'
    if 'apple' in text or 'iphone' in text:
        return 'apple'
    if 'canon' in text:
        return 'canon'
    if 'nikon' in text:
        return 'nikon'
    if 'sony' in text:
        return 'sony'
    if 'fujifilm' in text or 'fuji' in text:
        return 'fujifilm'
    if 'xiaomi' in text:
        return 'xiaomi'
    if 'huawei' in text:
        return 'huawei'
    if 'google' in text or 'pixel' in text:
        return 'google'
    return 'other'


def normalize_software_type(software: str) -> str:
    if not software or software == 'None':
        return 'none'

    s = software.strip().lower()

    # 편집 툴
    if 'photoshop' in s or 'lightroom' in s or 'gimp' in s or 'snapseed' in s:
        return 'editor'

    # AI 생성 툴
    if (
        'stable diffusion' in s or 'midjourney' in s or 'dall-e' in s or
        'dalle' in s or 'firefly' in s or 'novelai' in s or
        'comfyui' in s or 'automatic1111' in s or 'invokeai' in s or
        'leonardo' in s or 'gemini' in s or 'chatgpt' in s or 'openai' in s
    ):
        return 'ai'

    # 카메라/펌웨어 느낌
    if s.startswith('s9') or s.startswith('sm-') or 'iphone' in s or 'canon' in s or 'nikon' in s:
        return 'camera_fw'

    return 'unknown'


def compute_entropy(gray: np.ndarray) -> float:
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    prob = hist / (hist.sum() + 1e-12)
    prob = prob[prob > 0]
    return float(-np.sum(prob * np.log2(prob)))


def compute_high_freq_energy(gray: np.ndarray) -> float:
    """간단한 고주파 성분 비율"""
    gray = gray.astype(np.float32)
    fft = np.fft.fft2(gray)
    fft_shift = np.fft.fftshift(fft)
    magnitude = np.abs(fft_shift)

    h, w = gray.shape
    cy, cx = h // 2, w // 2
    r = min(h, w) // 8  # 중앙 저주파 영역 반경

    y, x = np.ogrid[:h, :w]
    dist2 = (y - cy) ** 2 + (x - cx) ** 2
    low_freq_mask = dist2 <= r * r

    total_energy = np.sum(magnitude) + 1e-12
    high_freq_energy = np.sum(magnitude[~low_freq_mask])

    return float(high_freq_energy / total_energy)


def detect_prompt_like_text(text: str) -> int:
    t = text.lower()
    return int(any(hint in t for hint in AI_VALUE_HINTS))


def extract_metadata(image_source, label=-1) -> Dict[str, Any]:
    """
    이미지 1장에서 feature를 추출해 딕셔너리로 반환
    image_source: 파일 경로(str) 또는 bytes
    """
    filename = os.path.basename(image_source) if isinstance(image_source, str) else 'image_from_bytes'
    file_ext = os.path.splitext(filename)[1].lower()

    result = {
        # 기본
        'filename': filename,
        'label': label,

        # 메타데이터 존재 여부
        'has_exif': 0,
        'has_camera': 0,
        'has_png_chunk': 0,
        'has_prompt': 0,
        'has_xmp': 0,

        # 세부 EXIF 존재 여부
        'has_make': 0,
        'has_model': 0,
        'has_datetime': 0,
        'has_gps': 0,
        'has_iso': 0,
        'has_exposure_time': 0,
        'has_fnumber': 0,
        'has_focal_length': 0,
        'has_orientation': 0,
        'has_color_space': 0,

        # 문자열/범주
        'make_raw': 'None',
        'model_raw': 'None',
        'camera_brand': 'none',
        'software_raw': 'None',
        'software_type': 'none',

        # 파일 구조
        'file_size': 0,
        'width': 0,
        'height': 0,
        'aspect_ratio': 0.0,
        'channels': 0,
        'is_jpeg': 0,
        'is_png': 0,
        'is_webp': 0,
        'mega_pixels': 0.0,
        'size_per_megapixel': 0.0,

        # 픽셀 통계
        'mean_r': 0.0,
        'mean_g': 0.0,
        'mean_b': 0.0,
        'std_r': 0.0,
        'std_g': 0.0,
        'std_b': 0.0,
        'mean_gray': 0.0,
        'std_gray': 0.0,
        'entropy': 0.0,
        'laplacian_var': 0.0,
        'high_freq_energy': 0.0,

        # 파생 feature
        'metadata_empty': 1,
        'exif_but_no_camera': 0,
        'camera_but_no_datetime': 0,
        'jpg_without_exif': 0,
        'png_with_exif': 0,
    }

    try:
        # 파일 크기
        if isinstance(image_source, str) and os.path.exists(image_source):
            result['file_size'] = os.path.getsize(image_source)

        source = io.BytesIO(image_source) if isinstance(image_source, bytes) else image_source

        with Image.open(source) as img:
            # 포맷/크기
            width, height = img.size
            result['width'] = width
            result['height'] = height
            result['aspect_ratio'] = round(width / height, 6) if height else 0.0

            fmt = (img.format or '').upper()
            result['is_jpeg'] = int(fmt in ('JPEG', 'JPG') or file_ext in ('.jpg', '.jpeg'))
            result['is_png'] = int(fmt == 'PNG' or file_ext == '.png')
            result['is_webp'] = int(fmt == 'WEBP' or file_ext == '.webp')

            mp = (width * height) / 1_000_000 if width and height else 0.0
            result['mega_pixels'] = round(mp, 6)
            result['size_per_megapixel'] = round(result['file_size'] / mp, 6) if mp > 0 else 0.0

            # 채널 수
            mode_to_channels = {
                '1': 1, 'L': 1, 'P': 1,
                'RGB': 3, 'RGBA': 4,
                'CMYK': 4, 'YCbCr': 3,
                'LAB': 3, 'HSV': 3,
                'I': 1, 'F': 1
            }
            result['channels'] = mode_to_channels.get(img.mode, 0)

            # -------------------------
            # 1) EXIF 확인
            # -------------------------
            exif_data = img.getexif()
            if exif_data and len(exif_data) > 0:
                result['has_exif'] = 1

                for tag_id, value in exif_data.items():
                    tag_name = EXIF_TAGS.get(tag_id, tag_id)

                    if tag_name == 'Make':
                        result['has_make'] = 1
                        result['make_raw'] = str(value).strip()
                    elif tag_name == 'Model':
                        result['has_model'] = 1
                        result['model_raw'] = str(value).strip()
                    elif tag_name in ('DateTime', 'DateTimeOriginal', 'DateTimeDigitized'):
                        result['has_datetime'] = 1
                    elif tag_name == 'Software':
                        result['software_raw'] = str(value).strip()
                    elif tag_name in ('ISOSpeedRatings', 'PhotographicSensitivity'):
                        result['has_iso'] = 1
                    elif tag_name == 'ExposureTime':
                        result['has_exposure_time'] = 1
                    elif tag_name == 'FNumber':
                        result['has_fnumber'] = 1
                    elif tag_name == 'FocalLength':
                        result['has_focal_length'] = 1
                    elif tag_name == 'Orientation':
                        result['has_orientation'] = 1
                    elif tag_name == 'ColorSpace':
                        result['has_color_space'] = 1
                    elif tag_name == 'GPSInfo' and value:
                        result['has_gps'] = 1

                result['has_camera'] = int(result['has_make'] == 1 or result['has_model'] == 1)

            # -------------------------
            # 2) PNG info / 텍스트 청크 확인
            # -------------------------
            info = getattr(img, 'info', {}) or {}
            if info:
                info_keys = {str(key).lower() for key in info.keys()}

                # 텍스트 청크 존재
                if AI_TEXT_KEYS & info_keys:
                    result['has_png_chunk'] = 1
                    result['has_prompt'] = 1

                # key/value 둘 다 검사
                for key, value in info.items():
                    key_lower = str(key).lower()
                    value_text = str(value).strip()

                    if key_lower in AI_TEXT_KEYS:
                        result['has_png_chunk'] = 1
                        if value_text:
                            result['has_prompt'] = 1

                    if key_lower == 'software':
                        result['software_raw'] = value_text if value_text else result['software_raw']
                        result['has_png_chunk'] = 1

                    # 값 안에 AI 관련 흔적이 있으면 prompt 흔적
                    if value_text and detect_prompt_like_text(value_text):
                        result['has_png_chunk'] = 1
                        result['has_prompt'] = 1

            # -------------------------
            # 3) XMP 확인
            # -------------------------
            if hasattr(img, 'getxmp'):
                try:
                    xmp_data = img.getxmp()
                    if xmp_data:
                        result['has_xmp'] = 1
                        xmp_text = str(xmp_data).lower()

                        # 생성 도구 이름 추정
                        if 'midjourney' in xmp_text:
                            result['software_raw'] = 'Midjourney'
                        elif 'dall-e' in xmp_text or 'dalle' in xmp_text:
                            result['software_raw'] = 'DALL-E'
                        elif 'firefly' in xmp_text:
                            result['software_raw'] = 'Adobe Firefly'
                        elif 'novelai' in xmp_text:
                            result['software_raw'] = 'NovelAI'
                        elif 'stable diffusion' in xmp_text:
                            result['software_raw'] = 'Stable Diffusion'
                        elif 'comfyui' in xmp_text:
                            result['software_raw'] = 'ComfyUI'

                        if detect_prompt_like_text(xmp_text):
                            result['has_prompt'] = 1
                except Exception:
                    pass

        # -------------------------
        # 4) 픽셀 통계 (OpenCV)
        # -------------------------
        if isinstance(image_source, str):
            img_bgr = cv2.imdecode(np.fromfile(image_source, dtype=np.uint8), cv2.IMREAD_COLOR)
        else:
            img_bgr = cv2.imdecode(np.frombuffer(image_source, dtype=np.uint8), cv2.IMREAD_COLOR)

        if img_bgr is not None:
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

            # 채널 평균/표준편차
            result['mean_r'] = round(float(np.mean(img_rgb[:, :, 0])), 6)
            result['mean_g'] = round(float(np.mean(img_rgb[:, :, 1])), 6)
            result['mean_b'] = round(float(np.mean(img_rgb[:, :, 2])), 6)

            result['std_r'] = round(float(np.std(img_rgb[:, :, 0])), 6)
            result['std_g'] = round(float(np.std(img_rgb[:, :, 1])), 6)
            result['std_b'] = round(float(np.std(img_rgb[:, :, 2])), 6)

            result['mean_gray'] = round(float(np.mean(gray)), 6)
            result['std_gray'] = round(float(np.std(gray)), 6)
            result['entropy'] = round(compute_entropy(gray), 6)

            lap = cv2.Laplacian(gray, cv2.CV_64F)
            result['laplacian_var'] = round(float(lap.var()), 6)

            result['high_freq_energy'] = round(compute_high_freq_energy(gray), 6)

        # -------------------------
        # 5) 범주/파생 feature
        # -------------------------
        result['camera_brand'] = normalize_camera_brand(result['make_raw'], result['model_raw'])
        result['software_type'] = normalize_software_type(result['software_raw'])

        metadata_signals = [
            result['has_exif'],
            result['has_xmp'],
            result['has_prompt'],
            result['has_png_chunk'],
            result['has_make'],
            result['has_model'],
            result['has_datetime'],
            result['has_gps'],
            result['has_iso'],
            result['has_exposure_time'],
        ]
        result['metadata_empty'] = int(sum(metadata_signals) == 0)
        result['exif_but_no_camera'] = int(result['has_exif'] == 1 and result['has_camera'] == 0)
        result['camera_but_no_datetime'] = int(result['has_camera'] == 1 and result['has_datetime'] == 0)
        result['jpg_without_exif'] = int(result['is_jpeg'] == 1 and result['has_exif'] == 0)
        result['png_with_exif'] = int(result['is_png'] == 1 and result['has_exif'] == 1)

    except Exception as e:
        print(f'[WARN] {filename} 처리 중 오류: {e}')

    return result


def collect_images_from_folder(folder_path, label):
    """폴더 내 이미지들을 순회하며 feature 추출"""
    if not os.path.exists(folder_path):
        print(f'[WARN] 폴더가 없습니다: {folder_path}')
        return []

    results = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(IMAGE_EXTENSIONS):
            image_path = os.path.join(folder_path, filename)
            row = extract_metadata(image_path, label)
            results.append(row)

    return results


def save_to_csv(rows, output_file='metadata_dataset.csv'):
    """추출 결과를 CSV로 저장"""
    if not rows:
        print('추출할 이미지가 없습니다.')
        return

    # 전체 필드 순서 고정
    fieldnames = [
        'filename', 'label',

        'has_exif', 'has_camera', 'has_png_chunk', 'has_prompt', 'has_xmp',
        'has_make', 'has_model', 'has_datetime', 'has_gps', 'has_iso',
        'has_exposure_time', 'has_fnumber', 'has_focal_length',
        'has_orientation', 'has_color_space',

        'make_raw', 'model_raw', 'camera_brand',
        'software_raw', 'software_type',

        'file_size', 'width', 'height', 'aspect_ratio', 'channels',
        'is_jpeg', 'is_png', 'is_webp', 'mega_pixels', 'size_per_megapixel',

        'mean_r', 'mean_g', 'mean_b',
        'std_r', 'std_g', 'std_b',
        'mean_gray', 'std_gray', 'entropy',
        'laplacian_var', 'high_freq_energy',

        'metadata_empty', 'exif_but_no_camera', 'camera_but_no_datetime',
        'jpg_without_exif', 'png_with_exif'
    ]

    with open(output_file, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f'총 {len(rows)}개의 이미지 데이터가 저장되었습니다: {output_file}')


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    REAL_FOLDER = os.path.join(base_dir, 'train_datasets', 'real')
    AI_FOLDER = os.path.join(base_dir, 'train_datasets', 'ai')

    # real: 0, ai: 1
    all_data = []
    all_data.extend(collect_images_from_folder(REAL_FOLDER, label=0))
    all_data.extend(collect_images_from_folder(AI_FOLDER, label=1))

    output_csv = os.path.join(base_dir, 'model', 'metadata_dataset_expanded.csv')
    save_to_csv(all_data, output_csv)