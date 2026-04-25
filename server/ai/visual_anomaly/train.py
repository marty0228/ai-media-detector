import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import mlflow
import mlflow.pytorch

try:
    from ai.visual_anomaly.model import VisualAnomalyResNet
except ModuleNotFoundError:
    from model import VisualAnomalyResNet

# 배포된 Cloud Run 주소 설정
MLFLOW_TRACKING_URI = "https://mlflow-server-7852824563.asia-northeast3.run.app"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("AI_Media_Detector_Visual_Anomaly")

# ── 설정 변수 (추후 변경 가능) ──
DATA_DIR = os.path.join(os.path.dirname(__file__), "datasets")
MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), "visual_anomaly.pth")
BATCH_SIZE = 32
NUM_EPOCHS = 10
LEARNING_RATE = 0.001

def train_model():
    print("Setting up device...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # 1. 데이터 검증
    train_dir = os.path.join(DATA_DIR, "train")
    test_dir = os.path.join(DATA_DIR, "test")
    
    if not os.path.exists(train_dir) or not os.path.exists(test_dir):
        print(f"오류: 학습(train) 또는 평가(test) 데이터셋 폴더가 없습니다!")
        print(f"필요 경로: {train_dir}, {test_dir}")
        print("각 폴더 하위 구조로 'real'과 'ai' 폴더를 만들어 이미지를 분리해 넣어주세요.")
        return

    # 2. 전처리 파이프라인 (Train vs Test 분리)
    train_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    test_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(), # 검증/평가 시에는 회전, 뒤집기 등 데이터 증강(Augmentation)을 하지 않습니다!
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # 3. 데이터 로더 명시적 분리 로드
    try:
        train_dataset = datasets.ImageFolder(train_dir, train_transforms)
        test_dataset = datasets.ImageFolder(test_dir, test_transforms)
        
        class_names = train_dataset.classes
        print(f"Classes found: {class_names}")  # 일반적으로 ['ai', 'real'] 알파벳순

        train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)
        val_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2)
        
        print(f"Total images - Train: {len(train_dataset)}, Test(Val): {len(test_dataset)}")
    except Exception as e:
        print(f"데이터셋 로드 실패: {e}")
        return

    # 4. 모델 셋업
    print("Initializing ResNet50 model...")
    model = VisualAnomalyResNet(pretrained=True)
    model.freeze_feature_layers() # 최초에는 Classifier만 학습
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    # 학습 가능한(classifier) 파라미터만 optimizer에 전달
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=LEARNING_RATE)

    # 5. 훈련 루프
    print(f"Starting training for {NUM_EPOCHS} epochs...")
    
    with mlflow.start_run():
        mlflow.log_params({
            "model_type": "ResNet50_VisualAnomaly",
            "batch_size": BATCH_SIZE,
            "num_epochs": NUM_EPOCHS,
            "learning_rate": LEARNING_RATE
        })

        for epoch in range(NUM_EPOCHS):
            # ===== 학습(Train) 단계 =====
            model.train()
            train_running_loss = 0.0
            train_corrects = 0
            train_total = 0
            
            for inputs, labels in train_loader:
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                loss = criterion(outputs, labels)

                loss.backward()
                optimizer.step()

                train_running_loss += loss.item() * inputs.size(0)
                train_corrects += torch.sum(preds == labels.data)
                train_total += inputs.size(0)

            train_loss = train_running_loss / train_total
            train_acc = train_corrects.double() / train_total

            # ===== 검증(Validation) 단계 =====
            model.eval()
            val_running_loss = 0.0
            val_corrects = 0
            val_total = 0

            with torch.no_grad():
                for inputs, labels in val_loader:
                    inputs = inputs.to(device)
                    labels = labels.to(device)

                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    val_running_loss += loss.item() * inputs.size(0)
                    val_corrects += torch.sum(preds == labels.data)
                    val_total += inputs.size(0)

            val_loss = val_running_loss / val_total
            val_acc = val_corrects.double() / val_total

            print(f"Epoch {epoch+1}/{NUM_EPOCHS} - "
                  f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
                  f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f}")
            
            mlflow.log_metrics({
                "train_loss": float(train_loss),
                "train_accuracy": float(train_acc),
                "val_loss": float(val_loss),
                "val_accuracy": float(val_acc)
            }, step=epoch+1)

        # 6. 모델 저장
        print(f"Training complete. Saving model to {MODEL_SAVE_PATH}")
        torch.save(model.state_dict(), MODEL_SAVE_PATH)
        
        # 모델 저장 (자동으로 GCS 버킷에 업로드됨)
        mlflow.pytorch.log_model(model, "resnet_model")

if __name__ == "__main__":
    train_model()
