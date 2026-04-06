"""
AI 이미지 생성 플랫폼 도메인 블랙리스트 및 AI 관련 키워드 목록.
Web Detection 결과에서 AI 생성 이미지 여부를 판별하는 데 사용됩니다.
"""

# AI 이미지 생성 플랫폼 도메인 목록
# URL에 이 도메인이 포함되면 AI 생성 이미지일 가능성이 높음
AI_DOMAINS = {
    # 주요 AI 이미지 생성 플랫폼
    "midjourney.com",
    "dall-e.com",
    "openai.com/dall-e",
    "labs.openai.com",
    "leonardo.ai",
    "playground.ai",
    "dreamstudio.ai",
    "stability.ai",
    "stablediffusionweb.com",
    "nightcafe.studio",
    "craiyon.com",
    "deepai.org",
    "hotpot.ai",
    "pixlr.com/image-generator",

    # AI 아트 커뮤니티 / 갤러리
    "civitai.com",
    "lexica.art",
    "openart.ai",
    "prompthero.com",
    "arthub.ai",
    "aiartshop.com",

    # AI 이미지 호스팅 / 공유
    "cdn.midjourney.com",
    "mj-gallery.com",
    "diffusionart.co",
}

# 페이지 제목이나 Web Entity에서 AI 생성 여부를 판별하기 위한 키워드
# 대소문자 무시하여 비교
AI_KEYWORDS = [
    "ai generated",
    "ai-generated",
    "ai art",
    "ai image",
    "midjourney",
    "dall-e",
    "dall·e",
    "dalle",
    "stable diffusion",
    "generative ai",
    "text to image",
    "text-to-image",
    "ai 생성",
    "ai 이미지",
    "인공지능 생성",
    "image generator",
    "ai artwork",
    "deepfake",
    "synthetically generated",
    "machine generated",
]
