import base64
import io
import random
import time
import cv2
import numpy as np
import qrcode
import serial
from PIL import Image
from flask import request
from sqlalchemy.exc import SQLAlchemyError

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


def create_qr_code(trash_type, user_id, logo_path='app/static/logo.png', fill_color="#2795EF", back_color="white"):
    """QR 코드 생성, 고해상도 지원 및 중앙에 로고 오버레이"""
    try:
        # 기본 유효성 검사
        if not trash_type or not user_id:
            raise ValueError("유효하지 않은 분류 정보 또는 사용자 ID입니다.")

        # QR 코드 데이터 설정
        qr_data = f"{user_id}:{trash_type}"
        qr = qrcode.QRCode(
            version=5,  # 데이터 밀도를 높이기 위해 QR 코드 크기 조정
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # 높은 오류 보정률 사용
            box_size=10,  # 블록 크기를 높여 해상도 증가
            border=4,  # 여백 유지
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # QR 코드 이미지 생성 및 색상 설정
        img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")

        # 로고 이미지 로드 및 크기 조정
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = min(img.size) // 6  # QR 코드 크기의 1/6로 로고 크기 조정
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

        # QR 코드 중앙에 로고를 배치
        pos = ((img.size[0] - logo_size) // 2, (img.size[1] - logo_size) // 2)
        img.paste(logo, pos, mask=logo)

        # 고해상도 출력: 이미지 크기 확대
        upscale_factor = 2  # 2배 확대
        img = img.resize((img.size[0] * upscale_factor, img.size[1] * upscale_factor), Image.Resampling.LANCZOS)

        # 이미지를 base64로 인코딩
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"

    except Exception as e:
        # 오류 발생 시 오류 메시지를 반환
        return {"error": f"QR 코드 생성 중 오류 발생: {str(e)}"}


# 포인트 적립(true - 적립 성공, false - 적립 실패)
def update_user_points(user_id, trash_type, trash_boolean, points=None):
    """사용자 포인트를 적립하고 재활용 로그를 기록하는 서비스 함수"""
    try:
        # 사용자 조회
        user = User.query.get(user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        # 포인트 적립 여부 결정
        points_to_add = points if points else random.randint(1, 15) if trash_boolean else 0
        user.points += points_to_add if trash_boolean else 0

        # 재활용 로그 생성 (is_successful 값 설정)
        recycle_log = RecycleLog(
            user_id=user.id,
            trash_type=trash_type,
            recycle_count=1,
            earned_points=points_to_add,
            is_successful=trash_boolean  # 쓰레기 투입 여부
        )

        # 데이터베이스에 추가 및 커밋
        db.session.add(recycle_log)
        db.session.commit()

        # 성공 또는 실패 메시지 생성
        if trash_boolean:
            success_message = f"{points_to_add} 포인트가 적립되었습니다."
        else:
            success_message = "쓰레기가 투입되지 않아 포인트가 적립되지 않았습니다."

        return points_to_add, success_message

    except SQLAlchemyError as e:
        db.session.rollback()  # 데이터베이스 오류 시 롤백
        print(f"Database error: {e}")
        raise


# 쓰레기 투입됐는지 확인
def get_latest_points_status(user_id):
    """사용자의 최신 포인트 적립 상태를 조회하는 서비스 함수"""
    try:
        # 사용자 조회
        user = User.query.get(user_id)
        if not user:
            return {"message": "사용자를 찾을 수 없습니다.", "success": False}

        # 가장 최근의 재활용 로그 조회
        recycle_log = RecycleLog.query.filter_by(user_id=user_id).order_by(RecycleLog.timestamp.desc()).first()

        # 변동이 없는 경우: last_checked_at이 최신 로그의 timestamp보다 이후인 경우
        if user.last_checked_at and recycle_log and user.last_checked_at >= recycle_log.timestamp:
            return {
                "message": "아직 쓰레기 투입 안됨",
                "success": False,
            }

        # 변동이 있는 경우, 최신 재활용 로그 정보 반환 및 last_checked_at 갱신
        if recycle_log:
            earned_points = recycle_log.earned_points
            success = recycle_log.earned_points > 0
            message = "포인트 적립 완료" if success else "쓰레기 투입 실패로 포인트 미적립"

            # last_checked_at을 최신 로그의 timestamp로 업데이트
            user.last_checked_at = recycle_log.timestamp
            db.session.commit()

            return {
                "message": message,
                "earned_points": earned_points,
                "success": success,
            }

        # 재활용 기록이 없는 경우
        return {"message": "포인트 적립 기록 없음", "success": False}

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return {"message": "서버 오류가 발생했습니다.", "success": False}


def get_event_stream(user_id):
    """사용자의 포인트 적립 상태를 실시간으로 스트리밍"""
    # 사용자 조회
    user = User.query.get(user_id)
    if not user:
        yield f"data: {{\"message\": \"사용자를 찾을 수 없습니다.\"}}\n\n"
        return

    while True:
        # 가장 최근의 재활용 로그 조회
        recycle_log = RecycleLog.query.filter_by(user_id=user_id).order_by(RecycleLog.timestamp.desc()).first()

        # 변동이 있는 경우, 최신 재활용 로그 정보 반환
        if recycle_log and (not user.last_checked_at or user.last_checked_at < recycle_log.timestamp):
            user.last_checked_at = recycle_log.timestamp  # last_checked_at 갱신
            db.session.commit()

            # SSE 형식으로 메시지 생성
            earned_points = recycle_log.earned_points
            success = recycle_log.earned_points > 0
            message = "포인트 적립 완료" if success else "쓰레기 투입 실패로 포인트 미적립"

            yield f"data: {{\"message\": \"{message}\", \"earned_points\": {earned_points}, \"success\": {success}, \"timestamp\": \"{recycle_log.timestamp.isoformat()}\"}}\n\n"

        # 일정 시간 대기 (polling 주기 대체)
        time.sleep(2)  # 2초 대기