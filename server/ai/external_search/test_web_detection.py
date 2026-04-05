from google.cloud import vision

def main():
    client = vision.ImageAnnotatorClient()

    try:
        with open("test.jpg", "rb") as f:
            content = f.read()
    except FileNotFoundError:
        print("test.jpg 파일을 현재 폴더에서 찾을 수 없습니다.")
        return

    image = vision.Image(content=content)

    response = client.web_detection(image=image)
    web_detection = response.web_detection

    if response.error.message:
        print("API 오류:", response.error.message)
        return

    print("=== Web Entities ===")
    for entity in web_detection.web_entities:
        print(f"설명: {entity.description}, 점수: {entity.score}")

    print("\n=== Pages With Matching Images ===")
    for page in web_detection.pages_with_matching_images:
        print(page.url)

    print("\n=== Full Matching Images ===")
    for img in web_detection.full_matching_images:
        print(img.url)

    print("\n=== Partial Matching Images ===")
    for img in web_detection.partial_matching_images:
        print(img.url)

    print("\n=== Visually Similar Images ===")
    for img in web_detection.visually_similar_images:
        print(img.url)

if __name__ == "__main__":
    main()