import base64
import io
import json
import random
import threading

import cv2
import numpy as np
import qrcode
from PIL import Image
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session, sessionmaker

from app import db
from app.models.recycle_log import RecycleLog
from app.models.user import User
from app.models.yolo_model import model

clients_lock = threading.Lock()
clients = {}


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
        clients[user_id] = {'event': event}

    try:
        # 이벤트 발생 대기
        event.wait()
        print(f"[DEBUG] Event triggered for user_id={user_id}")

        # 최신 데이터 조회
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
                    print(f"[DEBUG] Sending SSE data: {data}")
                    yield f"data: {json.dumps(data)}\n\n"

                    # 연결 종료 이벤트 추가
                    yield "event: close\ndata: Connection closed\n\n"
                else:
                    print(f"[ERROR] No recycle log found for user_id={user_id}")
            except Exception as e:
                print(f"[ERROR] Database error: {e}")
                yield f"data: {json.dumps({'error': 'Database error'})}\n\n"
            finally:
                session.remove()
    except GeneratorExit:
        print(f"[DEBUG] SSE connection closed for user_id={user_id}")
    finally:
        with clients_lock:
            del clients[user_id]
            print(f"[DEBUG] Client removed for user_id={user_id}")


def detect(image):
    """ONNX 모델로 물체를 분류하고 해당 분류를 반환합니다."""
    try:
        image_np = np.frombuffer(image.read(), np.uint8)
        frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        input_image = cv2.resize(frame, (640, 640))
        input_image = input_image.transpose(2, 0, 1)
        input_image = input_image[np.newaxis, :, :, :].astype(np.float32) / 255.0

        outputs = model.run(None, {'images': input_image})
        print("ONNX 모델 추론 결과 구조:", outputs)

        trash_type = None
        for prediction in outputs[0][0]:
            class_probs = prediction[-3:]
            label = int(np.argmax(class_probs))
            trash_type = {0: 'Can', 1: 'Plastic', 2: 'Paper'}.get(label, 'Unknown')
            break

        return trash_type
    except Exception as e:
        print(f"물체 분류 오류 발생: {e}")
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
