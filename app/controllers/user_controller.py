from flask import jsonify
from app.services.user_service import get_user_home_info, get_user_points


# 사용자 홈 화면 정보 조회 API
def get_user_home_info_controller(user_id):
    result, status_code = get_user_home_info(user_id)
    return jsonify(result), status_code


# 사용자 포인트 조회 컨트롤러
def get_user_points_controller(user_id):
    points_info, status_code = get_user_points(user_id)
    return jsonify(points_info), status_code
