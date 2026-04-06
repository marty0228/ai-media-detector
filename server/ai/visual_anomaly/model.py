import torch
import torch.nn as nn
from torchvision import models

class VisualAnomalyResNet(nn.Module):
    def __init__(self, pretrained=True):
        super(VisualAnomalyResNet, self).__init__()
        
        # 1. ResNet50 로드 (weights 매개변수를 이용하는 최신 PyTorch 방식 대응, 구버전은 pretrained=True 처리)
        try:
            from torchvision.models import ResNet50_Weights
            self.model = models.resnet50(weights=ResNet50_Weights.DEFAULT if pretrained else None)
        except ImportError:
            self.model = models.resnet50(pretrained=pretrained)
        
        # 2. 마지막 분류기(Classifier) 수정
        # 원본 ResNet50의 마지막 레이어(fc)의 입력 크기(in_features) 유지
        num_ftrs = self.model.fc.in_features
        
        # 이진 분류 (0: Real, 1: AI)용으로 fc 레이어 교체
        self.model.fc = nn.Sequential(
            nn.Dropout(p=0.5), # 과적합 방지
            nn.Linear(num_ftrs, 2)
        )
        
    def forward(self, x):
        return self.model(x)

    def freeze_feature_layers(self):
        """특징 추출기(feature extractor) 부분의 가중치를 고정하고 마지막 분류기(fc)만 학습합니다."""
        for name, param in self.model.named_parameters():
            if "fc" not in name:
                param.requires_grad = False
                
    def unfreeze_all_layers(self):
        """Fine-tuning을 위해 모든 레이어의 가중치를 학습 가능 상태로 바꿉니다."""
        for param in self.parameters():
            param.requires_grad = True
