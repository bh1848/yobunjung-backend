import onnxruntime as ort
import numpy as np
import cv2

def load_model():
    # ONNX 모델 경로를 설정
    model_path = "app/models/best.onnx"
    return ort.InferenceSession(model_path)  # ONNX Runtime 모델 세션 생성

def detect(image, model):
    # 이미지 전처리
    input_image = cv2.resize(image, (640, 640))
    input_image = input_image.transpose(2, 0, 1)  # 채널 우선
    input_image = input_image[np.newaxis, :, :, :].astype(np.float32) / 255.0

    # 추론 실행
    outputs = model.run(None, {'images': input_image})
    return outputs

# 모델 인스턴스 생성
model = load_model()
