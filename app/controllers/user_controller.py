from flask import jsonify
from app.services.user_service import get_user_home_info, get_user_recycle_logs, get_user_points_logs


# 사용자 홈 화면 정보 조회
def get_user_home_info_controller(user_id):
    result, status_code = get_user_home_info(user_id)
    return jsonify(result), status_code


# 현재 사용자의 재활용 내역 조회
def get_user_recycle_logs_controller(user_id):
    recycle_logs, status_code = get_user_recycle_logs(user_id)
    return jsonify(recycle_logs), status_code

# 사용자 포인트 사용 내역 조회
def user_points_logs_controller(user_id):
    """사용자 포인트 로그 조회 컨트롤러"""
    response, status_code = get_user_points_logs(user_id)
    return jsonify(response), status_code
