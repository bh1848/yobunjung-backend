from flask import request, jsonify

from app.services.recycle_service import (
    create_qr_code,
    detect,
    update_user_points
)

# qr 생성
def create_qr_controller(trash_type, user_id):
    """QR 코드를 생성하고, Base64로 인코딩된 QR 코드를 반환합니다."""
    if not trash_type or not user_id:
        raise ValueError("유효하지 않은 분류 정보 또는 사용자 ID입니다.")
    return create_qr_code(trash_type, user_id)


# 쓰레기 사진 인식
def detect_controller(image):
    """이미지에서 물체를 분류하고 결과를 반환합니다."""
    trash_type = detect(image)
    if not trash_type:
        raise ValueError("물체 분류 실패")
    return trash_type


# 포인트 적립
def add_user_points_controller():
    """사용자의 포인트를 적립하고 결과를 반환하는 컨트롤러"""
    data = request.get_json()
    user_id = data.get("user_id")
    trash_type = data.get("trash_type")
    trash_boolean = data.get("trash_boolean")
    # 쓰레기 투입 여부를 나타내는 boolean 값

    # 필요한 데이터가 누락된 경우
    if not user_id or not trash_type or trash_boolean is None:
        return jsonify({"error": "user_id, trash_type, trash_boolean을 제공해야 합니다."}), 400

    # 쓰레기가 실제로 투입된 경우에만 포인트 적립
    if trash_boolean:
        try:
            points_added = update_user_points(user_id, trash_type)
            return jsonify({"message": "포인트가 적립되었습니다.", "points_added": points_added}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 404  # 사용자 없음
        except Exception as e:
            return jsonify({"error": "포인트 적립 중 오류 발생"}), 500  # 기타 오류
    else:
        return jsonify({"message": "쓰레기가 투입되지 않았습니다. 포인트가 적립되지 않았습니다."}), 200
