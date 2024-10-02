from flask import Blueprint, request

from app.controllers.auth_controller import login_controller, logout_controller, register_controller

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# 로그인 엔드포인트
@auth_bp.route('/login', methods=['POST'])
def login_route():
    data = request.json
    return login_controller(data)


# 로그아웃 엔드포인트
@auth_bp.route('/logout', methods=['POST'])
def logout_route():
    return logout_controller()


# 회원가입
@auth_bp.route('/register', methods=['POST'])
def register_route():
    data = request.json
    return register_controller(data)
