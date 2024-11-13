import pytz
from sqlalchemy import DateTime

from app import db


class RecycleLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trash_type = db.Column(db.String(50), nullable=False)
    recycle_count = db.Column(db.Integer, default=0)
    earned_points = db.Column(db.Integer, default=0)
    timestamp = db.Column(DateTime(timezone=True), default=db.func.now())  # UTC로 저장
    is_successful = db.Column(db.Boolean, default=False)  # 쓰레기 투입 여부를 나타내는 boolean 필드

    @property
    def timestamp_kst(self):
        # UTC 시간대를 명시적으로 설정 후 KST로 변환
        if self.timestamp is not None:
            kst = pytz.timezone('Asia/Seoul')
            return self.timestamp.replace(tzinfo=pytz.utc).astimezone(kst)
        return None

    # 사용자와의 관계 설정 (back_populates 사용)
    user = db.relationship('User', back_populates='recycle_logs')
