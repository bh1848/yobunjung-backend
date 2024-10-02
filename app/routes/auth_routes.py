from flask import Blueprint, request, jsonify
from app.controllers.auth_controller import login_user, logout_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# 로그인 엔드포인트
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    return jsonify(login_user(data))


# 로그아웃 엔드포인트
@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify(logout_user())
