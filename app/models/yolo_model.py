import torch
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module='torch.cuda.amp.autocast')


# 모델 로드 함수
def load_model():
    model_path = '/home/ubuntu/yobunjung/Flask/exp6/weights/best.pt'  # 절대 경로 사용
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True, trust_repo=True)
    model.to(device)
    return model


# 모델 인스턴스 생성
model = load_model()
