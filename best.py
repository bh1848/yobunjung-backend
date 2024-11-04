import torch
from yolov5.models.common import DetectMultiBackend  # YOLOv5 모델이 설치된 경로에 맞게 수정하세요

# 기존 모델 파일을 로드합니다
model = torch.hub.load('ultralytics/yolov5', 'custom', path='exp6/weights/best.pt', force_reload=True)

# 모델의 state_dict(가중치)만 저장하여 새로운 파일로 생성
torch.save(model.state_dict(), 'exp6/weights/best_linux.pt')
