from flask import jsonify, request
from app.services.trash_service import TrashService
from flask_login import current_user


# 이미지 처리 요청
def process_trash_image_controller():
    image = request.files.get('image')
    if not image:
        return jsonify({"msg": "이미지가 제공되지 않았습니다."}), 400

    response, status_code = TrashService.process_trash_image(current_user, image)
    return jsonify(response), status_code


# QR 코드 검증 요청
def validate_qr_code_controller():
    data = request.json
    qr_code = data.get('qr_code')
    if not qr_code:
        return jsonify({"msg": "QR 코드가 제공되지 않았습니다."}), 400

    response, status_code = TrashService.validate_qr_code(current_user, qr_code)
    return jsonify(response), status_code
