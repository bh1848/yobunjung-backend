from flask import jsonify
from app.services.trash_service import process_trash_image, validate_qr_code


def process_image(user, image):
    """
    사용자가 업로드한 이미지를 처리하고 쓰레기 인식을 통해 QR 코드 생성
    """
    return jsonify(process_trash_image(user, image))


def scan_qr(user, qr_code):
    """
    QR 코드 인식 후 쓰레기 처리가 완료되면 포인트를 지급
    """
    return jsonify(validate_qr_code(user, qr_code))
