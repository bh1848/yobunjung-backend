# routes.py
from flask import Blueprint, request, jsonify
from app.controllers.recycle_controller import (
    create_qr_controller,
    detect_controller,
    send_bin_signal_controller,
    update_user_points_controller
)

recycle_bp = Blueprint('recycle', __name__, url_prefix='/recycle')

@recycle_bp.route('/create_qr', methods=['POST'])
def create_qr():
    data = request.get_json()
    classification = data.get('classification')
    user_id = data.get('user_id')

    try:
        qr_code_b64 = create_qr_controller(classification, user_id)
        return jsonify({"qr_code": qr_code_b64}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "QR 코드 생성 중 오류 발생"}), 500

@recycle_bp.route('/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return jsonify({"error": "이미지 파일이 필요합니다."}), 400

    image = request.files['image']
    try:
        classification = detect_controller(image)
        return jsonify({"classification": classification}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "물체 분류 중 오류 발생"}), 500

@recycle_bp.route('/send_bin_signal', methods=['POST'])
def send_signal():
    data = request.get_json()
    bin_type = data.get('bin_type')

    try:
        send_bin_signal_controller(bin_type)
        return jsonify({"message": f"{bin_type} 신호가 성공적으로 전송되었습니다."}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "아두이노 신호 전송 중 오류 발생"}), 500

@recycle_bp.route('/update_points', methods=['POST'])
def update_points():
    data = request.get_json()
    user_id = data.get('user_id')
    bin_type = data.get('bin_type')

    try:
        points_added = update_user_points_controller(user_id, bin_type)
        return jsonify({"message": "포인트 적립 성공", "points_added": points_added}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "포인트 적립 중 오류 발생"}), 500
