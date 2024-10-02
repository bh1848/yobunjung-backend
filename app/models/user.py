from flask_login import UserMixin
from app import db  # db를 사용하기 전에 app/__init__.py에서 먼저 초기화되도록 보장


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    nickname = db.Column(db.String(50), unique=True, nullable=False)
    points = db.Column(db.Integer, default=0)

    # RecycleLog와의 관계 설정 (back_populates 사용)
    recycle_logs = db.relationship('RecycleLog', back_populates='user')

    def set_password(self, password):
        # 비밀번호 설정 (해시 사용 가능)
        self.password = password

    def check_password(self, password):
        # 비밀번호 검증
        return self.password == password
