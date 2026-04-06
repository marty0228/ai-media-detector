from ultralytics import YOLO

if __name__ == '__main__':
  # 1. 모델 로드 (가장 가벼운 Nano 버전 사용)
  model = YOLO('yolov8n.pt') 

  # 2. 모델 학습
  # data.yaml에는 데이터셋 경로와 클래스 정보(0: watermark)가 들어있어야 합니다.
  model.train(
    data='./datasets/data.yaml', 
    epochs=1, 
    imgsz=640, 
    device=0,
    project='watermark_model',
    name='final_v1',
    exist_ok=True
  )
   

  # 3. 학습된 모델 저장
  #model.export(format='pt')

