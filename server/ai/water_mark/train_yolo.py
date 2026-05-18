import os
from pathlib import Path

from ultralytics import YOLO

if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent
    data_path = base_dir / 'datasets' / 'data.yaml'
    project_dir = base_dir / 'runs' / 'detect'

    epochs = int(os.getenv('WATERMARK_EPOCHS', '50'))
    imgsz = int(os.getenv('WATERMARK_IMGSZ', '640'))
    device = os.getenv('WATERMARK_DEVICE', '0')

    # 1. 모델 로드 (가장 가벼운 Nano 버전 사용)
    model = YOLO('yolov8n.pt')

    # 2. 모델 학습
    # data.yaml에는 데이터셋 경로와 클래스 정보(0: watermark)가 들어있어야 합니다.
    model.train(
        data=str(data_path),
        epochs=epochs,
        imgsz=imgsz,
        device=device,
        project=str(project_dir),
        name='final_v1',
        exist_ok=True,
    )

    # 3. 학습된 모델 저장
    # model.export(format='pt')

