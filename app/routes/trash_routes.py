from flask import Blueprint, request, jsonify
from app.controllers.trash_controller import process_image, scan_qr

trash_bp = Blueprint('trash', __name__, url_prefix='/trash')


# 이미지 업로드 및 쓰레기 처리
@trash_bp.route('/upload', methods=['POST'])
def upload_image():
    user = request.user  # 로그인한 사용자 정보
    image = request.files['image']  # 업로드된 이미지
    return process_image(user, image)

# QR 코드 스캔
@trash_bp.route('/scan', methods=['POST'])
def scan_qr_code():
    user = request.user  # 로그인한 사용자 정보
    qr_code = request.json.get('qr_code')
    return scan_qr(user, qr_code)
