from flask import Blueprint, request, jsonify
from app.controllers.recycle_controller import (
    create_qr_controller,
    add_user_points_controller, stream_sse, handle_detection
)

recycle_bp = Blueprint('recycle', __name__, url_prefix='/recycle')


# qr생성
@recycle_bp.route('/create_qr', methods=['POST'])
def create_qr():
    data = request.get_json()
    trash_type = data.get('trash_type')
    user_id = data.get('user_id')

    try:
        qr_code_b64 = create_qr_controller(trash_type, user_id)
        return jsonify({"qr_code": qr_code_b64}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "QR 코드 생성 중 오류 발생"}), 500


# 쓰레기사진인식
@recycle_bp.route('/detect', methods=['POST'])
def detect_route():
    return handle_detection()


# 포인트 적립 엔드포인트
@recycle_bp.route('/add_points', methods=['POST'])
def user_add_points():
    return add_user_points_controller()


# SSE 스트림 엔드포인트
@recycle_bp.route('/<int:user_id>/is_successful', methods=['GET'])
def stream(user_id):
    """SSE 엔드포인트"""
    return stream_sse(user_id)
