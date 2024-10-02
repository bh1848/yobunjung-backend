from app.models.user import User
from flask import session


class AuthService:

    @staticmethod
    def login(email, password):
        # 사용자 조회
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # 로그인 성공 -> 세션에 사용자 정보 저장
            session['user_id'] = user.id
            session['user_name'] = user.name
            return {"message": "로그인 성공", "user_name": user.name}, 200
        else:
            return {"message": "로그인 실패. 이메일 또는 비밀번호를 확인하세요."}, 401

    @staticmethod
    def logout():
        # 세션에서 사용자 정보 제거
        session.pop('user_id', None)
        session.pop('user_name', None)
        return {"message": "로그아웃 성공"}, 200

    @staticmethod
    def dashboard():
        if 'user_id' not in session:
            return {"message": "로그인이 필요합니다."}, 403
        return {"message": f"환영합니다, {session['user_name']}님!"}, 200
