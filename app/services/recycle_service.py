import io
import base64
import random
import cv2
import qrcode
import numpy as np
import serial

from app.models.user import User
from app.models.recycle_log import RecycleLog
from app.models.yolo_model import model  # yolo_model.py의 model 사용
from app import db

# Arduino 설정
arduino_port = '/dev/ttyACM0'
baud_rate = 9600
try:
    arduino = serial.Serial(arduino_port, baud_rate)
except serial.SerialException:
    arduino = None
    print("Arduino에 연결할 수 없습니다.")


def detect(image):
    """ONNX 모델로 물체를 분류하고 해당 분류를 반환합니다."""
    try:
        # 이미지를 numpy 배열로 읽어서 전처리
        image_np = np.frombuffer(image.read(), np.uint8)
        frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        input_image = cv2.resize(frame, (640, 640))
        input_image = input_image.transpose(2, 0, 1)  # 채널 우선
        input_image = input_image[np.newaxis, :, :, :].astype(np.float32) / 255.0

        # ONNX 추론 실행
        outputs = model.run(None, {'images': input_image})

        # 결과 구조 확인
        print("ONNX 모델 추론 결과 구조:", outputs)

        # ONNX 모델 출력에서 클래스 확률을 추출
        classification = None
        for prediction in outputs[0][0]:  # 첫 번째 예측 결과의 각 행을 반복
            # 각 예측 행에서 클래스 확률 값들을 추출 (마지막 3개의 값이 클래스 확률이라고 가정)
            class_probs = prediction[-3:]  # 클래스 확률 값 추출

            # 클래스 확률 중 가장 높은 값의 인덱스를 클래스 레이블로 사용
            label = int(np.argmax(class_probs))
            classification = {0: 'Can', 1: 'Plastic', 2: 'Paper'}.get(label, 'Unknown')
            break  # 첫 번째 유효한 예측만 사용

        return classification
    except Exception as e:
        print(f"물체 분류 오류 발생: {e}")
        return None

# QR 코드 생성
def create_qr_code(classification, user_id):
    """QR 코드 생성 및 base64로 인코딩된 이미지를 반환합니다."""
    if not classification or not user_id:
        raise ValueError("유효하지 않은 분류 정보 또는 사용자 ID입니다.")
    qr_data = f"{user_id}:{classification}"
    qr = qrcode.make(qr_data)
    buffered = io.BytesIO()
    qr.save(buffered, format="JPEG")
    return f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"


# 사용자 포인트 적립 및 로그 기록
def update_user_points(user_id, bin_type, points=None):
    """포인트를 적립하고 재활용 로그를 기록합니다."""
    user = User.query.get(user_id)
    if not user:
        raise ValueError("사용자를 찾을 수 없습니다.")

    points_to_add = points if points else random.randint(1, 15)
    user.points += points_to_add

    recycle_log = RecycleLog(
        user_id=user.id,
        bin_type=bin_type,
        recycle_count=1,
        earned_points=points_to_add
    )
    db.session.add(recycle_log)
    db.session.commit()
    return points_to_add


# 아두이노 신호 전송
def send_bin_signal(bin_type):
    """분류에 따라 아두이노로 신호를 전송합니다."""
    if arduino and arduino.is_open:
        signal = {'Can': b'CAN\n', 'Plastic': b'PLASTIC\n', 'Paper': b'PAPER\n'}.get(bin_type)
        if signal:
            arduino.write(signal)
        else:
            print("유효하지 않은 분류입니다.")
    else:
        print("Arduino에 연결할 수 없습니다.")


# QR 데이터 파싱
def process_qr_data(qr_data):
    """QR 코드 데이터를 파싱하여 사용자 ID와 분류를 반환합니다."""
    try:
        user_id, bin_type = qr_data.split(":")
        return user_id, bin_type
    except ValueError:
        raise ValueError("QR 코드 데이터 형식이 잘못되었습니다.")
