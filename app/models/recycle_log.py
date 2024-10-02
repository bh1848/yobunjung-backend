from app import db


class RecycleLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bin_type = db.Column(db.String(50), nullable=False)
    recycle_count = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    earned_points = db.Column(db.Integer, default=0)

    # 사용자와의 관계 설정 (back_populates 사용)
    user = db.relationship('User', back_populates='recycle_logs')
