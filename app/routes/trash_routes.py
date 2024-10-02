from flask import Blueprint
from app.controllers.trash_controller import (
    process_trash_image_controller,
    validate_qr_code_controller
)

trash_bp = Blueprint('trash', __name__, url_prefix='/trash')


# 이미지 업로드 처리
@trash_bp.route('/process_image', methods=['POST'])
def process_trash_image_route():
    return process_trash_image_controller()


# QR 코드 검증
@trash_bp.route('/validate_qr', methods=['POST'])
def validate_qr_code_route():
    return validate_qr_code_controller()
