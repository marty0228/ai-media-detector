import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from ai.visual_anomaly.model import VisualAnomalyResNet

# ── 설정 변수 (추후 변경 가능) ──
DATA_DIR = os.path.join(os.path.dirname(__file__), "dataset")
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
    if not os.path.exists(train_dir):
        print(f"오류: 데이터셋 폴더가 없습니다! ({train_dir})")
        print("하위 폴더 구조로 'real'과 'ai' 폴더를 파고 이미지를 넣어주세요.")
        return

    # 2. 전처리 파이프라인
    data_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # 3. 데이터 로더
    try:
        train_dataset = datasets.ImageFolder(train_dir, data_transforms)
        train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)
        class_names = train_dataset.classes
        print(f"Classes found: {class_names}")  # 일반적으로 ['ai', 'real'] 알파벳순
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
    model.train()
    
    for epoch in range(NUM_EPOCHS):
        running_loss = 0.0
        corrects = 0
        total = 0
        
        for inputs, labels in train_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            corrects += torch.sum(preds == labels.data)
            total += inputs.size(0)

        epoch_loss = running_loss / total
        epoch_acc = corrects.double() / total

        print(f"Epoch {epoch+1}/{NUM_EPOCHS} - Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")

    # 6. 모델 저장
    print(f"Training complete. Saving model to {MODEL_SAVE_PATH}")
    torch.save(model.state_dict(), MODEL_SAVE_PATH)

if __name__ == "__main__":
    train_model()
