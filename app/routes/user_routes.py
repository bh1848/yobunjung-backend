from flask import Blueprint
from app.controllers.user_controller import get_user_home_info_controller, get_user_points_controller

user_bp = Blueprint('user', __name__, url_prefix='/user')


# 사용자 홈 화면 정보 조회 라우트
@user_bp.route('/<int:user_id>/home', methods=['GET'])
def get_user_home_info_route(user_id):
    return get_user_home_info_controller(user_id)


# 사용자 포인트 조회 라우트
@user_bp.route('/<int:user_id>/points', methods=['GET'])
def get_user_points_route(user_id):
    return get_user_points_controller(user_id)
