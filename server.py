from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image, ExifTags, UnidentifiedImageError
import io
import hashlib
import random


app = FastAPI(title="AI Authenticator Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


AI_HINT_KEYWORDS = [
    "midjourney",
    "stable diffusion",
    "dall-e",
    "openai",
    "firefly",
    "generated",
    "ai",
]

EDIT_SOFTWARE_KEYWORDS = [
    "photoshop",
    "lightroom",
    "adobe",
    "gimp",
    "canva",
]


def clamp(value: int, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, value))


def safe_text(value, fallback="MISSING") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def extract_exif_dict(image: Image.Image) -> dict:
    try:
        raw_exif = image.getexif()
        if not raw_exif:
            return {}
    except Exception:
        return {}

    exif_data = {}
    for key, value in raw_exif.items():
        tag_name = ExifTags.TAGS.get(key, str(key))
        if isinstance(value, bytes):
            continue
        exif_data[tag_name] = value
    return exif_data


def make_rng_from_bytes(content: bytes) -> random.Random:
    digest = hashlib.sha256(content).hexdigest()
    seed = int(digest[:16], 16)
    return random.Random(seed)


def contains_keyword(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


def build_factor(
    title: str,
    subtitle: str,
    score: int,
    accent: str,
    progress_label: str,
    progress_value: str,
    metrics: list[dict],
    description: str,
) -> dict:
    return {
        "title": title,
        "subtitle": subtitle,
        "score": score,
        "accent": accent,
        "progressLabel": progress_label,
        "progressValue": progress_value,
        "metrics": metrics,
        "description": description,
    }


def analyze_provenance(exif_data: dict, rng: random.Random) -> dict:
    software = safe_text(exif_data.get("Software"))
    score = 52

    if not exif_data:
        score += 10

    if software != "MISSING":
        score += 8

    if contains_keyword(software, AI_HINT_KEYWORDS):
        score += 18
    elif contains_keyword(software, EDIT_SOFTWARE_KEYWORDS):
        score += 10

    score += rng.randint(-4, 6)
    score = clamp(score)

    if score >= 75:
        progress_value = "Weak Provenance"
    elif score >= 60:
        progress_value = "Limited Provenance"
    else:
        progress_value = "Moderate Provenance"

    description = (
        "This prototype checks whether creation-history-like traces or software "
        "hints are available. It does not yet validate real C2PA credentials."
    )

    return build_factor(
        title="Provenance Verification",
        subtitle="Origin & History",
        score=score,
        accent="#006a60",
        progress_label="Trust Index",
        progress_value=progress_value,
        metrics=[
            {"label": "Credential Status", "value": "NOT SUPPORTED YET"},
            {"label": "Software Trail", "value": software},
        ],
        description=description,
    )


def analyze_metadata(exif_data: dict, rng: random.Random) -> dict:
    make = safe_text(exif_data.get("Make"))
    model = safe_text(exif_data.get("Model"))
    software = safe_text(exif_data.get("Software"))

    score = 35

    if not exif_data:
        score += 24

    if make == "MISSING" and model == "MISSING":
        score += 12

    if software != "MISSING":
        score += 8

    if contains_keyword(software, AI_HINT_KEYWORDS):
        score += 12

    score += rng.randint(-4, 5)
    score = clamp(score)

    if score >= 70:
        progress_value = "Suspicious"
    elif score >= 50:
        progress_value = "Partially Available"
    else:
        progress_value = "Consistent"

    exif_status = "PRESENT" if exif_data else "MISSING"

    description = (
        "Metadata is treated as an independent factor. Missing EXIF, limited "
        "camera information, or software traces can increase the score."
    )

    return build_factor(
        title="Metadata Analysis",
        subtitle="EXIF & Headers",
        score=score,
        accent="#ffb780",
        progress_label="Header Integrity",
        progress_value=progress_value,
        metrics=[
            {"label": "Camera Model", "value": f"{make} / {model}"},
            {"label": "EXIF Status", "value": exif_status},
        ],
        description=description,
    )


def analyze_external_search(rng: random.Random) -> dict:
    score = clamp(52 + rng.randint(-6, 10))

    if score >= 65:
        progress_value = "Low Source Match"
    else:
        progress_value = "Pending Review"

    description = (
        "Reverse-image-search style validation is not connected yet. This field "
        "exists so the frontend can later receive real cross-source evidence."
    )

    return build_factor(
        title="External Search Validation",
        subtitle="Cross-Source Search",
        score=score,
        accent="#006a60",
        progress_label="Cross-Web Match",
        progress_value=progress_value,
        metrics=[
            {"label": "Search API", "value": "NOT CONNECTED"},
            {"label": "Source Trace", "value": "PENDING"},
        ],
        description=description,
    )


def analyze_visual(image: Image.Image, rng: random.Random) -> dict:
    width, height = image.size
    score = clamp(58 + rng.randint(0, 18))

    if width < 512 or height < 512:
        score += 4

    score = clamp(score)

    if score >= 75:
        progress_value = "Elevated"
    elif score >= 60:
        progress_value = "Moderate"
    else:
        progress_value = "Low"

    description = (
        "This is currently a prototype visual score placeholder. Later, this "
        "factor should be replaced with actual artifact detection logic."
    )

    return build_factor(
        title="Visual Anomaly Analysis",
        subtitle="Human-Readable Artifacts",
        score=score,
        accent="#ba1a1a",
        progress_label="Artifact Density",
        progress_value=progress_value,
        metrics=[
            {"label": "Resolution", "value": f"{width} x {height}"},
            {"label": "Review Mode", "value": "PROTOTYPE HEURISTIC"},
        ],
        description=description,
    )


def analyze_forensic(content: bytes, rng: random.Random) -> dict:
    file_hash = hashlib.sha256(content).hexdigest()[:8].upper()
    score = clamp(55 + rng.randint(0, 16))

    if len(content) < 300_000:
        score += 3

    score = clamp(score)

    if score >= 72:
        progress_value = "Detected"
    elif score >= 60:
        progress_value = "Moderate"
    else:
        progress_value = "Subtle"

    description = (
        "This field is reserved for future low-level analysis such as noise, "
        "compression, and pixel-pattern inconsistencies."
    )

    return build_factor(
        title="Forensic Pattern Analysis",
        subtitle="Noise & Compression Cues",
        score=score,
        accent="#264653",
        progress_label="Low-Level Signal",
        progress_value=progress_value,
        metrics=[
            {"label": "Hash Tag", "value": file_hash},
            {"label": "Compression Cue", "value": "REVIEW NEEDED"},
        ],
        description=description,
    )


def calculate_final_score(factors: list[dict]) -> float:
    weights = {
        "Provenance Verification": 0.30,
        "Metadata Analysis": 0.15,
        "External Search Validation": 0.20,
        "Visual Anomaly Analysis": 0.20,
        "Forensic Pattern Analysis": 0.15,
    }

    total = 0.0
    for factor in factors:
        weight = weights.get(factor["title"], 0.0)
        total += factor["score"] * weight

    return round(total, 1)


def build_summary(final_score: float, rng: random.Random) -> dict:
    if final_score >= 72:
        verdict = "LIKELY AI-GENERATED"
    elif final_score >= 56:
        verdict = "UNCERTAIN / REVIEW NEEDED"
    else:
        verdict = "LIKELY AUTHENTIC"

    confidence = round(0.82 + rng.random() * 0.13, 3)

    return {
        "finalScore": final_score,
        "verdict": verdict,
        "confidence": confidence,
        "description": (
            "This result is currently produced by a backend prototype pipeline. "
            "It already uses the five-factor structure, but some factors are still heuristic placeholders."
        ),
    }


def build_notes(filename: str, width: int, height: int) -> dict:
    return {
        "heroTitle": "Backend-Connected Prototype",
        "heroText": (
            "The dashboard is now receiving analysis data from FastAPI. "
            "Later, you can replace the placeholder scoring logic with real AI or forensic modules."
        ),
        "sideTitle": "Pipeline Status",
        "sideItems": [
            {"label": "Upload State", "value": "RECEIVED"},
            {"label": "Result Source", "value": "BACKEND"},
            {"label": "Factor Layout", "value": "5 FACTORS"},
            {"label": "Image Size", "value": f"{width}x{height}"},
            {"label": "File Name", "value": filename[:18]},
        ],
    }


@app.post("/analyze")
async def analyze_image(image: UploadFile = File(...)):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are allowed.")

    content = await image.read()

    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be 25MB or smaller.")

    try:
        pil_image = Image.open(io.BytesIO(content))
        pil_image.load()
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Invalid image file.")
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read image.")

    exif_data = extract_exif_dict(pil_image)
    rng = make_rng_from_bytes(content)

    provenance_factor = analyze_provenance(exif_data, rng)
    metadata_factor = analyze_metadata(exif_data, rng)
    external_factor = analyze_external_search(rng)
    visual_factor = analyze_visual(pil_image, rng)
    forensic_factor = analyze_forensic(content, rng)

    factors = [
        provenance_factor,
        metadata_factor,
        external_factor,
        visual_factor,
        forensic_factor,
    ]

    final_score = calculate_final_score(factors)
    summary = build_summary(final_score, rng)
    notes = build_notes(image.filename or "uploaded-image", pil_image.width, pil_image.height)

    return {
        "summary": summary,
        "factors": factors,
        "notes": notes,
    }


# IMPORTANT:
# analyze route must be declared BEFORE mounting static files.
app.mount("/", StaticFiles(directory=".", html=True), name="static")