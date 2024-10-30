import torch
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module='torch.cuda.amp.autocast')

# 모델 로드 함수
def load_model():
    # Linux와 Windows에서 호환되도록 추가 옵션 사용
    return torch.hub.load('ultralytics/yolov5', 'custom', path='exp6/weights/best.pt', force_reload=True, trust_repo=True)

# 모델 인스턴스 생성
model = load_model()
