import base64
import io
import json
import random
import threading
import os

import cv2
import numpy as np
import onnxruntime as ort
import qrcode
from PIL import Image
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session, sessionmaker

from app import db
from app.models.recycle_log import RecycleLog
from app.models.user import User

clients_lock = threading.Lock()
clients = {}


model_path = 'app/models/best.onnx'

try:
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {model_path}")

    session = ort.InferenceSession(model_path)
    print(f"[INFO] ONNX 모델이 성공적으로 로드되었습니다: {model_path}")
except FileNotFoundError as fnf_error:
    print(f"[ERROR] {fnf_error}")
except Exception as e:
    print(f"[ERROR] ONNX 모델 로드 실패: {e}")
    raise

# 클래스 이름 매핑
class_names = {0: 'Can', 1: 'Plastic', 2: 'Paper'}


def get_session():
    """세션 생성"""
    session_factory = sessionmaker(bind=db.engine)
    return scoped_session(session_factory)


def notify_client(user_id):
    """클라이언트에 알림 이벤트 트리거"""
    with clients_lock:
        if user_id in clients:
            try:
                clients[user_id]['event'].set()
                print(f"[DEBUG] Event set for user_id={user_id}")
            except Exception as e:
                print(f"[ERROR] Failed to notify client for user_id={user_id}: {e}")
        else:
            print(f"[DEBUG] No client registered for user_id={user_id}")


def get_event_stream(user_id):
    """SSE 이벤트 스트림 제공"""
    event = threading.Event()
    with clients_lock:
        # 기존 연결 초기화
        if user_id in clients:
            clients[user_id]['event'].set()
            del clients[user_id]
        clients[user_id] = {'event': event}

    try:
        while True:
            event.wait()  # 이벤트 발생 대기
            event.clear()  # 다음 이벤트를 위해 초기화

            with current_app.app_context():
                session = get_session()
                try:
                    recycle_log = (
                        session.query(RecycleLog)
                        .filter_by(user_id=user_id)
                        .order_by(RecycleLog.timestamp.desc())
                        .first()
                    )
                    if recycle_log:
                        data = {
                            'user_id': user_id,
                            'earned_points': recycle_log.earned_points,
                            'is_successful': recycle_log.is_successful,
                            'message': (
                                f"포인트가 적립되었습니다."
                                if recycle_log.is_successful
                                else "포인트가 적립되지 않았습니다."
                            ),
                        }
                        yield f"data: {json.dumps(data)}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
                finally:
                    session.remove()
    except GeneratorExit:
        print(f"[DEBUG] SSE connection closed for user_id={user_id}")
    finally:
        with clients_lock:
            if user_id in clients:
                del clients[user_id]
            print(f"[DEBUG] Client removed for user_id={user_id}")


def detect_objects(image):
    """
    ONNX 모델을 사용해 입력 이미지를 감지합니다.
    - 입력: OpenCV 이미지
    - 출력: 감지된 물체 정보 (가장 높은 confidence 기준)
    """
    try:
        # 모델 입력 이름 및 크기 가져오기
        input_name = session.get_inputs()[0].name
        input_shape = session.get_inputs()[0].shape  # [batch_size, channels, height, width]

        # 이미지 전처리
        input_image = cv2.resize(image, (input_shape[2], input_shape[3]))  # 크기 조정
        input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)  # 색 공간 변환
        input_image = input_image.transpose(2, 0, 1)  # HWC -> CHW
        input_image = np.expand_dims(input_image, axis=0).astype(np.float32) / 255.0  # 정규화 및 배치 추가

        # 모델 추론
        outputs = session.run(None, {input_name: input_image})

        # 감지 결과 처리
        detections = []
        output_data = outputs[0][0]  # 2차원 배열로 가정
        for detection in output_data:  # 각 감지 결과를 순회
            if len(detection) < 5:
                print(f"[WARN] 예상치 못한 출력 형식: {detection}")
                continue

            # 바운딩 박스와 클래스 확률 추출
            x1, y1, x2, y2, confidence = detection[:5]
            class_probs = detection[5:]
            label = int(np.argmax(class_probs))  # 가장 높은 확률의 클래스
            trash_type = class_names.get(label, 'Unknown')

            if confidence > 0.5:  # 신뢰도 임계값
                detections.append({
                    "trash_type": trash_type,
                    "confidence": float(confidence),
                    "box": [int(x1), int(y1), int(x2), int(y2)]
                })

        # 가장 높은 confidence 값 선택
        if detections:
            best_detection = max(detections, key=lambda x: x['confidence'])
            print(f"[DEBUG] 선택된 감지 결과: {best_detection}")
            return best_detection['trash_type']
        else:
            print("[DEBUG] 감지 결과가 없습니다.")
            return None

    except Exception as e:
        print(f"[ERROR] ONNX 감지 오류 발생: {e}")
        return None


def create_qr_code(trash_type, user_id, logo_path='app/static/logo.png', fill_color="#2795EF", back_color="white"):
    """QR 코드 생성, 고해상도 지원 및 중앙에 로고 오버레이"""
    try:
        if not trash_type or not user_id:
            raise ValueError("유효하지 않은 분류 정보 또는 사용자 ID입니다.")

        qr_data = f"{user_id}:{trash_type}"
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = min(img.size) // 6
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

        pos = ((img.size[0] - logo_size) // 2, (img.size[1] - logo_size) // 2)
        img.paste(logo, pos, mask=logo)

        upscale_factor = 2
        img = img.resize((img.size[0] * upscale_factor, img.size[1] * upscale_factor), Image.Resampling.LANCZOS)

        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"

    except Exception as e:
        print(f"QR 코드 생성 중 오류 발생: {e}")
        return {"error": f"QR 코드 생성 중 오류 발생: {str(e)}"}


def update_user_points(user_id, trash_type, trash_boolean, points=None):
    """사용자 포인트를 적립하고 재활용 로그를 기록하는 서비스 함수"""
    try:
        user = User.query.get(user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        points_to_add = points if points else random.randint(1, 15) if trash_boolean else 0
        user.points += points_to_add if trash_boolean else 0

        recycle_log = RecycleLog(
            user_id=user.id,
            trash_type=trash_type,
            recycle_count=1,
            earned_points=points_to_add,
            is_successful=trash_boolean
        )

        db.session.add(recycle_log)
        db.session.commit()

        # SSE 이벤트 트리거
        notify_client(user_id)

        if trash_boolean:
            success_message = f"{points_to_add} 포인트가 적립되었습니다."
        else:
            success_message = "쓰레기가 투입되지 않아 포인트가 적립되지 않았습니다."

        return points_to_add, success_message

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error: {e}")
        raise
