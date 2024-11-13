import pytz
from flask_login import UserMixin
from sqlalchemy import DateTime

from app import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    nickname = db.Column(db.String(50), unique=True, nullable=False)
    points = db.Column(db.Integer, default=0)
    last_checked_at = db.Column(DateTime(timezone=True), default=db.func.now())  # UTC로 저장

    @property
    def last_checked_kst(self):
        """last_checked_at을 KST로 변환하여 반환"""
        if self.last_checked_at is not None:
            kst = pytz.timezone('Asia/Seoul')
            return self.last_checked_at.replace(tzinfo=pytz.utc).astimezone(kst)
        return None

    # RecycleLog와의 관계 설정 (back_populates 사용)
    recycle_logs = db.relationship('RecycleLog', back_populates='user')

    def set_password(self, password):
        # 비밀번호 설정 (해시 사용 가능)
        self.password = password

    def check_password(self, password):
        # 비밀번호 검증
        return self.password == password
