from flask_login import login_user, logout_user, current_user

from app import db
from app.models.recycle_log import RecycleLog
from app.models.user import User


class AuthService:

    # 로그인
    @staticmethod
    def login(email, password):
        # 사용자 조회
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)  # 세션에 사용자 정보 저장
            return {"message": "로그인 성공", "user_name": user.name}, 200
        else:
            return {"message": "로그인 실패. 이메일 또는 비밀번호를 확인하세요."}, 401

    # 로그아웃
    @staticmethod
    def logout():
        # Flask-Login의 logout_user를 사용하여 세션에서 사용자 정보 제거
        logout_user()
        return {"message": "로그아웃 성공"}, 200

    # 대시보드 접근
    @staticmethod
    def dashboard():
        # current_user를 사용하여 로그인 여부 확인
        if not current_user.is_authenticated:
            return {"message": "로그인이 필요합니다."}, 403
        return {"message": f"환영합니다, {current_user.name}님!"}, 200

    # 회원가입
    @staticmethod
    def register(email, password, name, nickname):
        # 필수 데이터 확인
        if not email or not password or not name or not nickname:
            return {"message": "모든 필드를 입력해주세요."}, 400

        # 이메일 중복 확인
        if User.query.filter_by(email=email).first():
            return {"message": "이미 사용 중인 이메일입니다."}, 400

        # 새 사용자 생성
        new_user = User(email=email, name=name, nickname=nickname)
        new_user.set_password(password)  # 비밀번호 설정

        # 데이터베이스에 사용자 추가
        db.session.add(new_user)
        db.session.commit()

        # 회원가입 후 추가 작업: 기본 재활용 로그 생성
        recycle_log_paper = RecycleLog(user_id=new_user.id, bin_type='paper', recycle_count=0)
        recycle_log_plastic = RecycleLog(user_id=new_user.id, bin_type='plastic', recycle_count=0)
        recycle_log_can = RecycleLog(user_id=new_user.id, bin_type='can', recycle_count=0)

        # 추가 데이터 저장
        db.session.add(recycle_log_paper)
        db.session.add(recycle_log_plastic)
        db.session.add(recycle_log_can)
        db.session.commit()

        return {
            "message": "회원가입 성공",
            "user": {
                "email": new_user.email,
                "name": new_user.name,
                "nickname": new_user.nickname
            }
        }, 201
