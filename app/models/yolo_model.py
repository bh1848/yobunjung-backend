import torch
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module='torch.cuda.amp.autocast')


# 모델 로드 함수
def load_model():
    return torch.hub.load('ultralytics/yolov5', 'custom', path='exp6/weights/best.pt')


# 모델 인스턴스 생성
model = load_model()
