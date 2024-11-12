from flask import request, jsonify

from app.services.recycle_service import (
    create_qr_code,
    detect,
    update_user_points, get_latest_points_status
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
    """포인트 적립 요청을 처리하고 응답을 반환하는 컨트롤러"""
    data = request.get_json()
    user_id = data.get("user_id")
    trash_type = data.get("trash_type")
    trash_boolean = data.get("trash_boolean")

    # 필수 데이터가 누락된 경우 에러 반환
    if not user_id or not trash_type or trash_boolean is None:
        return jsonify({"error": "user_id, trash_type, trash_boolean을 제공해야 합니다."}), 400

    try:
        # 쓰레기 투입 여부가 참일 경우에만 포인트 적립 진행
        points_added, success_message = update_user_points(user_id, trash_type, trash_boolean)
        return jsonify({"message": success_message, "points_added": points_added}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404  # 사용자 없음
    except Exception as e:
        return jsonify({"error": "포인트 적립 중 오류 발생"}), 500  # 기타 오류


# 쓰레기 투입됐는지 확인
def check_points_status_controller(user_id):
    """사용자의 최신 포인트 적립 상태를 조회하는 컨트롤러"""
    if not user_id:
        return jsonify({"error": "user_id를 제공해야 합니다."}), 400

    # 서비스 계층에서 포인트 상태 조회
    result = get_latest_points_status(user_id)
    return jsonify(result), result.get("status_code", 200)