"""
Google Cloud Vision API Web Detection을 활용한 AI 이미지 판별 모듈.

full_matching_images, pages_with_matching_images, web_entities를 종합 분석하여
이미지가 AI 생성 플랫폼에서 유래했는지 판별합니다.
"""

from google.cloud import vision
from urllib.parse import urlparse
from ai.external_search.ai_domains import AI_DOMAINS, AI_KEYWORDS

# 모듈 레벨에서 클라이언트를 관리
_client = None


def load_model():
    """
    Vision API 클라이언트를 초기화합니다.
    """
    global _client
    print("Loading external_search model (Vision API client)...")
    _client = vision.ImageAnnotatorClient()
    print("Vision API client loaded.")


def _get_domain(url: str) -> str:
    """URL에서 도메인을 추출합니다."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return ""


def _is_ai_domain(url: str) -> bool:
    """URL이 AI 이미지 생성 플랫폼의 도메인인지 확인합니다."""
    domain = _get_domain(url)
    for ai_domain in AI_DOMAINS:
        # 서브도메인까지 포함하여 매칭 (예: cdn.midjourney.com → midjourney.com)
        if ai_domain in domain or ai_domain in url.lower():
            return True
    return False


def _check_ai_keywords(text: str) -> bool:
    """텍스트에 AI 관련 키워드가 포함되어 있는지 확인합니다."""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in AI_KEYWORDS)


def _analyze_web_detection(web_detection) -> dict:
    """
    Web Detection 결과를 Noisy-OR 독립 확률 결합 방식으로 분석하여
    AI 판별 점수를 산출합니다.
    """
    details = {
        "full_match_count": 0,
        "ai_domain_full_matches": [],
        "page_count": 0,
        "ai_domain_pages": [],
        "ai_keyword_pages": [],
        "ai_entities": [],
        "non_ai_sources": 0,
    }

    full_matches = list(web_detection.full_matching_images)
    details["full_match_count"] = len(full_matches)

    for img in full_matches:
        if _is_ai_domain(img.url):
            details["ai_domain_full_matches"].append(img.url)

    pages = list(web_detection.pages_with_matching_images)
    details["page_count"] = len(pages)

    for page in pages:
        url = page.url
        title = page.page_title if hasattr(page, "page_title") else ""

        if _is_ai_domain(url):
            details["ai_domain_pages"].append(url)
        elif title and not _is_ai_domain(url):
            details["non_ai_sources"] += 1

        if _check_ai_keywords(title) or _check_ai_keywords(url):
            details["ai_keyword_pages"].append({
                "url": url,
                "title": title
            })

    for entity in web_detection.web_entities:
        desc = entity.description if entity.description else ""
        if _check_ai_keywords(desc):
            details["ai_entities"].append({
                "description": desc,
                "score": entity.score
            })

    # ── 매칭 결과가 전혀 없는 경우: 70% 의심 ──
    if len(full_matches) == 0 and len(pages) == 0:
        return 0.5, details

    # ── 독립 확률(Noisy-OR) 확률값(x1, x2, x3, x4) 계산 ──
    # 전체 페이지 수에 비례해서 나누지 않고, 발견된 증거 하나하나를 독립적인 사건으로 간주합니다.
    
    # 1. AI 도메인 완전 일치 (개당 80% 확신)
    k1 = len(details["ai_domain_full_matches"])
    x1 = 1.0 - (1.0 - 0.80) ** k1

    # 2. AI 베이스 도메인 페이지 발견 (개당 70% 확신)
    k2 = len(details["ai_domain_pages"])
    x2 = 1.0 - (1.0 - 0.70) ** k2

    # 3. AI 키워드가 포함된 페이지 (개당 30% 확신)
    k3 = len(details["ai_keyword_pages"])
    x3 = 1.0 - (1.0 - 0.30) ** k3

    # 4. Web Entities 보조 지표
    x4 = 0.0
    if details["ai_entities"]:
        max_entity_score = max([e["score"] for e in details["ai_entities"]])
        x4 = 0.4 * max_entity_score  # 최대 40% 확신

    # ── 독립 확률 결합 (Noisy-OR) ──
    # P(AI) = 1 - (1 - P(x1)) * (1 - P(x2)) * (1 - P(x3)) * (1 - P(x4))
    score = 1.0 - ((1.0 - x1) * (1.0 - x2) * (1.0 - x3) * (1.0 - x4))

    score = max(0.0, min(1.0, score))

    return score, details


def predict(image_bytes: bytes) -> dict:
    """
    이미지 바이트를 받아 Web Detection 기반 AI 판별 결과를 반환합니다.
    """
    global _client

    # 클라이언트가 아직 초기화되지 않은 경우 초기화
    if _client is None:
        load_model()

    try:
        image = vision.Image(content=image_bytes)
        response = _client.web_detection(image=image)

        if response.error.message:
            print(f"Vision API error: {response.error.message}")
            return {
                "model_name": "external_search",
                "predicted_idx": 0,
                "confidence": 0.5,
                "details": {"error": response.error.message}
            }

        web_detection = response.web_detection
        score, details = _analyze_web_detection(web_detection)

        # 0.5 이상이면 AI로 판별
        predicted_idx = 1 if score >= 0.5 else 0

        return {
            "model_name": "external_search",
            "predicted_idx": predicted_idx,
            "confidence": round(score, 4),
            "details": details
        }

    except Exception as e:
        print(f"External search prediction error: {e}")
        return {
            "model_name": "external_search",
            "predicted_idx": 0,
            "confidence": 0.5,
            "details": {"error": str(e)}
        }
