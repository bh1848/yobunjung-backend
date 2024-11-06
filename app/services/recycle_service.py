import base64
import io
import random

import cv2
import numpy as np
import qrcode
import serial
from PIL import Image

from app import db
from app.models.recycle_log import RecycleLog
from app.models.user import User
from app.models.yolo_model import model

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
        trash_type = None
        for prediction in outputs[0][0]:  # 첫 번째 예측 결과의 각 행을 반복
            # 각 예측 행에서 클래스 확률 값들을 추출 (마지막 3개의 값이 클래스 확률이라고 가정)
            class_probs = prediction[-3:]  # 클래스 확률 값 추출

            # 클래스 확률 중 가장 높은 값의 인덱스를 클래스 레이블로 사용
            label = int(np.argmax(class_probs))
            trash_type = {0: 'Can', 1: 'Plastic', 2: 'Paper'}.get(label, 'Unknown')
            break  # 첫 번째 유효한 예측만 사용

        return trash_type
    except Exception as e:
        print(f"물체 분류 오류 발생: {e}")
        return None

# QR 코드 생성
def create_qr_code(trash_type, user_id, logo_path='app/static/logo.png', fill_color="#2795EF", back_color="white"):
    """QR 코드 생성, 중앙에 로고를 QR 코드 위에 오버레이하여 깔끔하게 삽입."""
    try:
        # 기본 유효성 검사
        if not trash_type or not user_id:
            raise ValueError("유효하지 않은 분류 정보 또는 사용자 ID입니다.")

        # QR 코드 데이터 설정
        qr_data = f"{user_id}:{trash_type}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # 높은 오류 보정률 사용
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # QR 코드 이미지 생성 및 색상 설정
        img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")

        # 로고 이미지 로드 및 흰색 배경을 투명하게 설정
        logo = Image.open(logo_path).convert("RGBA")
        datas = logo.getdata()

        new_data = []

        logo.putdata(new_data)

        # 로고 크기 조절
        logo_size = min(img.size) // 4  # QR 코드 크기의 1/4로 로고 크기 조정
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

        # QR 코드 중앙에 로고를 오버레이
        pos = ((img.size[0] - logo_size) // 2, (img.size[1] - logo_size) // 2)
        img.paste(logo, pos, mask=logo)  # 로고를 QR 코드 중앙에 배치

        # 이미지를 base64로 인코딩
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"

    except Exception as e:
        # 오류 발생 시 오류 메시지를 반환
        return {"error": f"QR 코드 생성 중 오류 발생: {str(e)}"}


# 사용자 포인트 적립 및 로그 기록
def update_user_points(user_id, trash_type, points=None):
    """포인트를 적립하고 재활용 로그를 기록합니다."""
    user = User.query.get(user_id)
    if not user:
        raise ValueError("사용자를 찾을 수 없습니다.")

    points_to_add = points if points else random.randint(1, 15)
    user.points += points_to_add

    recycle_log = RecycleLog(
        user_id=user.id,
        trash_type=trash_type,
        recycle_count=1,
        earned_points=points_to_add
    )
    db.session.add(recycle_log)
    db.session.commit()
    return points_to_add