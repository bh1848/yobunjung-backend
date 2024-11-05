from flask import Blueprint

from app.controllers.user_controller import get_user_home_info_controller, get_user_recycle_logs_controller, user_points_logs_controller

user_bp = Blueprint('user', __name__, url_prefix='/user')


# 홈 화면 user 정보 조회
@user_bp.route('/<int:user_id>/home', methods=['GET'])
def get_user_home_info_route(user_id):
    return get_user_home_info_controller(user_id)


# user 재활용 내역 조회
@user_bp.route('/<int:user_id>/recycle_logs', methods=['GET'])
def get_user_recycle_logs_route(user_id):
    return get_user_recycle_logs_controller(user_id)


# 사용자 포인트 로그 조회 엔드포인트
@user_bp.route('/<int:user_id>/points_logs', methods=['GET'])
def get_points_logs(user_id):
    return user_points_logs_controller(user_id)