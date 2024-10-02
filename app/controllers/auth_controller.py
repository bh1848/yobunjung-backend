from flask import session

from app.models.user import User


def login_user(data):
    """
    사용자 로그인 로직.
    """
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return {"msg": "잘못된 이메일 또는 비밀번호입니다."}, 401

    # 세션에 사용자 ID 저장
    session['user_id'] = user.id
    return {"msg": "로그인 성공", "user": {"email": user.email, "name": user.name}}, 200


def logout_user():
    """
    사용자 로그아웃 로직.
    """
    session.pop('user_id', None)  # 세션에서 사용자 ID 제거
    return {"msg": "로그아웃 성공"}, 200


def is_logged_in():
    """
    사용자가 로그인 상태인지 확인하는 로직.
    """
    if 'user_id' in session:
        return True
    return False
