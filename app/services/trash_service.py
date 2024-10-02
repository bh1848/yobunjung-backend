import datetime
import random

from app import db
from app.models.trash import TrashRecord
from app.utils.image_processor import is_trash_detected
from app.utils.qr_generator import generate_qr_code


def process_trash_image(user, image):
    """
    사용자가 업로드한 이미지를 처리하고 쓰레기인지 확인
    """
    if is_trash_detected(image):  # OpenCV로 쓰레기 인식
        qr_code = generate_qr_code(user.email)  # 사용자 이메일 기반으로 QR 코드 생성
        new_record = TrashRecord(user_id=user.id, qr_code=qr_code)
        db.session.add(new_record)
        db.session.commit()
        return {"msg": "쓰레기 인식 성공", "qr_code": qr_code}, 200
    else:
        return {"msg": "쓰레기가 아닙니다."}, 400


def validate_qr_code(user, qr_code):
    """
    쓰레기통에서 QR 코드를 인식하고 검증 후 포인트 지급 (랜덤으로 1~10 포인트)
    """
    record = TrashRecord.query.filter_by(qr_code=qr_code, user_id=user.id).first()
    if record and not record.processed_at:
        # 1~10 사이의 랜덤 포인트 지급
        random_points = random.randint(1, 10)
        user.points += random_points

        # 기록 업데이트
        record.processed_at = datetime.datetime.utcnow()
        record.points_awarded = random_points
        db.session.commit()

        return {"msg": f"쓰레기 처리 완료. {random_points} 포인트가 지급되었습니다.", "points": user.points}, 200
    return {"msg": "유효하지 않은 QR 코드입니다."}, 400
