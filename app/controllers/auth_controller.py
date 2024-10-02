from flask import jsonify
from flask_login import login_required

from app.services.auth_service import AuthService


# 로그인 컨트롤러
def login_controller(data):
    email = data.get('email')
    password = data.get('password')
    response, status = AuthService.login(email, password)
    return jsonify(response), status


# 로그아웃 컨트롤러
@login_required  # Flask-Login 데코레이터로 로그아웃 시 로그인이 요구됨
def logout_controller():
    response, status = AuthService.logout()
    return jsonify(response), status


# 회원가입 컨트롤러
def register_controller(data):
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    nickname = data.get('nickname')
    response, status = AuthService.register(email, password, name, nickname)
    return jsonify(response), status
