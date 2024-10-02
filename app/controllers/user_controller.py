from flask import jsonify
from app.services.user_service import get_user_home_info


# 사용자 홈 화면 정보 조회 API
def get_user_home_info_controller(user_id):
    result, status_code = get_user_home_info(user_id)
    return jsonify(result), status_code
