from flask import request, jsonify
from app.services.trash_bin_service import update_trash_bin_status_by_fill_level

# 쓰레기통 포화도 변경
def update_trash_bin_fill_level_controller():
    """
    요청에서 trash_type과 fill_level을 받아 쓰레기통 상태를 업데이트하는 컨트롤러 함수입니다.
    """
    data = request.get_json()
    trash_type = data.get("trash_type")
    fill_level = data.get("fill_level")

    if trash_type is None or fill_level is None:
        return jsonify({"error": "trash_type과 fill_level이 필요합니다."}), 400

    # 서비스 함수 호출하여 상태 업데이트
    response, status_code = update_trash_bin_status_by_fill_level(trash_type, fill_level)
    return jsonify(response), status_code
