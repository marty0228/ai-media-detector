import os
import csv
import io
from typing import Any, Dict
from PIL import Image, ExifTags, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

# ---------------------------------------------------------
# 1. 전역 상수 및 설정 정의
# ---------------------------------------------------------
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp')
AI_TEXT_KEYS = {'parameters', 'prompt', 'workflow', 'description', 'comment'}
AI_VALUE_HINTS = {
    'stable diffusion',
    'midjourney',
    'dall-e',
    'dalle',
    'firefly',
    'novelai',
    'comfyui',
    'automatic1111',
    'invokeai',
    'c2pa',
    'ai generated',
    'generated',
}
EXIF_TAGS = ExifTags.TAGS


# ---------------------------------------------------------
# 2. 범주형 데이터 정규화 헬퍼 함수
# ---------------------------------------------------------
def normalize_camera_brand(make: str, model: str) -> str:
    # 카메라 제조사 및 모델 문자열을 소문자 단일 브랜드명으로 일관되게 정규화
    t = f"{make} {model}".strip().lower()

    if not t:
        return 'none'

    for b in ['samsung', 'apple', 'canon', 'nikon', 'sony', 'fujifilm', 'xiaomi', 'huawei', 'google']:
        if (
            b in t
            or (b == 'samsung' and (t.startswith('sm-') or t.startswith('s9')))
            or (b == 'apple' and 'iphone' in t)
            or (b == 'fujifilm' and 'fuji' in t)
            or (b == 'google' and 'pixel' in t)
        ):
            return b

    return 'other'


def normalize_software_type(software: str) -> str:
    # 생성 또는 편집 소프트웨어 이름을 일반화된 카테고리로 분류
    s = str(software).strip().lower()

    if not s or s == 'none':
        return 'none'

    if any(k in s for k in ['photoshop', 'lightroom', 'gimp', 'snapseed']):
        return 'editor'

    if any(
        k in s
        for k in [
            'stable diffusion',
            'midjourney',
            'dall-e',
            'dalle',
            'firefly',
            'novelai',
            'comfyui',
            'automatic1111',
            'invokeai',
            'leonardo',
            'gemini',
            'chatgpt',
            'openai',
        ]
    ):
        return 'ai'

    if s.startswith('s9') or s.startswith('sm-') or any(k in s for k in ['iphone', 'canon', 'nikon']):
        return 'camera_fw'

    return 'unknown'


# ---------------------------------------------------------
# 3. 핵심 메타데이터 추출 메인 로직
# ---------------------------------------------------------
def extract_metadata(image_source, label=-1) -> Dict[str, Any]:
    # 단일 이미지의 메타데이터를 추출하여 딕셔너리로 반환
    filename = os.path.basename(image_source) if isinstance(image_source, str) else 'image_from_bytes'
    ext = os.path.splitext(filename)[1].lower()

    res = dict.fromkeys(
        [
            'has_exif',
            'has_camera',
            'has_png_chunk',
            'has_prompt',
            'has_xmp',
            'has_make',
            'has_model',
            'has_datetime',
            'has_gps',
            'has_iso',
            'has_exposure_time',
            'has_fnumber',
            'has_focal_length',
            'has_orientation',
            'has_color_space',
            'file_size',
            'width',
            'height',
            'channels',
            'is_jpeg',
            'is_png',
            'is_webp',
            'metadata_empty',
            'exif_but_no_camera',
            'camera_but_no_datetime',
            'jpg_without_exif',
            'png_with_exif',

            # -------------------------------------------------
            # 추가 feature 3개
            # -------------------------------------------------
            # EXIF 필드 개수
            'exif_field_count',

            # EXIF + PNG info + XMP 등 전체 메타데이터 key 개수
            'metadata_key_count',

            # PNG + EXIF 없음 + 카메라 없음 + 날짜 없음이면 스크린샷 성격으로 간주
            'is_screenshot_like',
        ],
        0,
    )

    res.update(
        {
            'aspect_ratio': 0.0,
            'mega_pixels': 0.0,
            'size_per_megapixel': 0.0,
            'make_raw': 'None',
            'model_raw': 'None',
            'camera_brand': 'none',
            'software_raw': 'None',
            'software_type': 'none',
            'filename': filename,
            'label': label,
        }
    )

    try:
        if isinstance(image_source, str) and os.path.exists(image_source):
            res['file_size'] = os.path.getsize(image_source)

        source = io.BytesIO(image_source) if isinstance(image_source, bytes) else image_source

        # =========================================================
        # 3.1 파일 구조 및 기본 속성 추출
        # =========================================================
        with Image.open(source) as img:
            w, h = img.size

            image_format = (img.format or '').upper()

            res.update(
                {
                    'width': w,
                    'height': h,
                    'aspect_ratio': round(w / h, 6) if h else 0.0,
                    'is_jpeg': int(image_format in ('JPEG', 'JPG') or ext in ('.jpg', '.jpeg')),
                    'is_png': int(image_format == 'PNG' or ext == '.png'),
                    'is_webp': int(image_format == 'WEBP' or ext == '.webp'),
                }
            )

            mp = (w * h) / 1_000_000
            res['mega_pixels'] = round(mp, 6)
            res['size_per_megapixel'] = round(res['file_size'] / mp, 6) if mp > 0 else 0.0

            res['channels'] = {
                '1': 1,
                'L': 1,
                'P': 1,
                'RGB': 3,
                'RGBA': 4,
                'CMYK': 4,
                'YCbCr': 3,
                'LAB': 3,
                'HSV': 3,
                'I': 1,
                'F': 1,
            }.get(img.mode, 0)

            # =========================================================
            # 3.2 카메라 EXIF 태그 파싱
            # =========================================================
            exif = img.getexif()

            if exif:
                res['has_exif'] = 1
                res['exif_field_count'] = len(exif)

                for tag_id, val in exif.items():
                    tag = EXIF_TAGS.get(tag_id, tag_id)

                    if tag == 'Make':
                        res.update({'has_make': 1, 'make_raw': str(val).strip()})

                    elif tag == 'Model':
                        res.update({'has_model': 1, 'model_raw': str(val).strip()})

                    elif tag in ('DateTime', 'DateTimeOriginal', 'DateTimeDigitized'):
                        res['has_datetime'] = 1

                    elif tag == 'Software':
                        res['software_raw'] = str(val).strip()

                    elif tag in ('ISOSpeedRatings', 'PhotographicSensitivity'):
                        res['has_iso'] = 1

                    elif tag == 'ExposureTime':
                        res['has_exposure_time'] = 1

                    elif tag == 'FNumber':
                        res['has_fnumber'] = 1

                    elif tag == 'FocalLength':
                        res['has_focal_length'] = 1

                    elif tag == 'Orientation':
                        res['has_orientation'] = 1

                    elif tag == 'ColorSpace':
                        res['has_color_space'] = 1

                    elif tag == 'GPSInfo' and val:
                        res['has_gps'] = 1

                res['has_camera'] = int(res['has_make'] or res['has_model'])

            # EXIF 필드 개수를 전체 메타데이터 key 개수에 반영
            res['metadata_key_count'] += res['exif_field_count']

            # =========================================================
            # 3.3 PNG/WEBP 내부 텍스트 청크 파싱
            # =========================================================
            info = img.info or {}
            info_keys = {str(k).lower() for k in info.keys()}

            # PNG info key 개수를 전체 메타데이터 key 개수에 반영
            res['metadata_key_count'] += len(info_keys)

            if AI_TEXT_KEYS & info_keys:
                res['has_png_chunk'] = 1
                res['has_prompt'] = 1

            for k, v in info.items():
                kl = str(k).lower()
                vt = str(v).strip()

                if kl in AI_TEXT_KEYS or (kl == 'software' and vt):
                    res['has_png_chunk'] = 1

                    if kl == 'software' and vt:
                        res['software_raw'] = vt

                    if kl in AI_TEXT_KEYS and vt:
                        res['has_prompt'] = 1

                if vt and any(h in vt.lower() for h in AI_VALUE_HINTS):
                    res['has_png_chunk'] = 1
                    res['has_prompt'] = 1

            # =========================================================
            # 3.4 어도비 XMP 확장 메타데이터 파싱
            # =========================================================
            if hasattr(img, 'getxmp'):
                xmp = img.getxmp()

                if xmp:
                    res['has_xmp'] = 1

                    # XMP key 개수를 전체 메타데이터 key 개수에 반영
                    if isinstance(xmp, dict):
                        res['metadata_key_count'] += len(xmp.keys())
                    else:
                        res['metadata_key_count'] += 1

                    xt = str(xmp).lower()

                    for tool in [
                        'midjourney',
                        'dall-e',
                        'dalle',
                        'firefly',
                        'novelai',
                        'stable diffusion',
                        'comfyui',
                    ]:
                        if tool in xt:
                            res['software_raw'] = tool.title() if tool not in ['dall-e', 'dalle'] else 'DALL-E'
                            break

                    if any(h in xt for h in AI_VALUE_HINTS):
                        res['has_prompt'] = 1

        # =========================================================
        # 3.5 추출된 데이터 파생 특징 계산 및 유효성 검증
        # =========================================================
        res['camera_brand'] = normalize_camera_brand(res['make_raw'], res['model_raw'])
        res['software_type'] = normalize_software_type(res['software_raw'])

        md_sigs = [
            res['has_exif'],
            res['has_xmp'],
            res['has_prompt'],
            res['has_png_chunk'],
            res['has_make'],
            res['has_model'],
            res['has_datetime'],
            res['has_gps'],
            res['has_iso'],
            res['has_exposure_time'],
        ]

        res['metadata_empty'] = int(not any(md_sigs))
        res['exif_but_no_camera'] = int(res['has_exif'] and not res['has_camera'])
        res['camera_but_no_datetime'] = int(res['has_camera'] and not res['has_datetime'])
        res['jpg_without_exif'] = int(res['is_jpeg'] and not res['has_exif'])
        res['png_with_exif'] = int(res['is_png'] and res['has_exif'])

        # ---------------------------------------------------------
        # 추가 feature: 스크린샷 성격 이미지 판별
        # ---------------------------------------------------------
        # 실제 스크린샷은 PNG이면서 EXIF/카메라/촬영 날짜가 없는 경우가 많음.
        # 이 feature는 "PNG + 메타데이터 없음 = 무조건 AI"로 학습되는 것을 줄이기 위한 보조 신호.
        res['is_screenshot_like'] = int(
            res['is_png']
            and not res['has_exif']
            and not res['has_camera']
            and not res['has_datetime']
        )

    except Exception as e:
        print(f'[WARN] {filename}: {e}')

    return res


# ---------------------------------------------------------
# 4. 파일 입출력 및 일괄 변환 데이터셋 생성 유틸리티
# ---------------------------------------------------------
def collect_images_from_folder(folder_path, label):
    # 폴더 내 모든 이미지를 순회하며 메타데이터 추출을 반복 적용
    if not os.path.exists(folder_path):
        return []

    return [
        extract_metadata(os.path.join(folder_path, f), label)
        for f in os.listdir(folder_path)
        if f.lower().endswith(IMAGE_EXTENSIONS)
    ]


def save_to_csv(rows, output_file='metadata_dataset.csv'):
    # 추출한 특징들 객체 배열을 머신러닝 학습이 가능하도록 CSV로 기록
    if not rows:
        return

    fieldnames = [
        'filename',
        'label',

        'has_exif',
        'has_camera',
        'has_png_chunk',
        'has_prompt',
        'has_xmp',
        'has_make',
        'has_model',
        'has_datetime',
        'has_gps',
        'has_iso',
        'has_exposure_time',
        'has_fnumber',
        'has_focal_length',
        'has_orientation',
        'has_color_space',

        'make_raw',
        'model_raw',
        'camera_brand',
        'software_raw',
        'software_type',

        'file_size',
        'width',
        'height',
        'aspect_ratio',
        'channels',
        'is_jpeg',
        'is_png',
        'is_webp',
        'mega_pixels',
        'size_per_megapixel',

        'metadata_empty',
        'exif_but_no_camera',
        'camera_but_no_datetime',
        'jpg_without_exif',
        'png_with_exif',

        # -------------------------------------------------
        # 추가 feature 3개
        # -------------------------------------------------
        'exif_field_count',
        'metadata_key_count',
        'is_screenshot_like',
    ]

    with open(output_file, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f'저장 완료: {output_file} ({len(rows)}개)')


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))

    data = (
        collect_images_from_folder(os.path.join(base_dir, 'train_datasets', 'real'), 0)
        + collect_images_from_folder(os.path.join(base_dir, 'train_datasets', 'ai'), 1)
    )

    save_to_csv(data, os.path.join(base_dir, 'model', 'metadata_dataset_expanded.csv'))