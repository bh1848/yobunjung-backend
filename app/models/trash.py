from app import db


class TrashRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    qr_code = db.Column(db.String(120), unique=True, nullable=False)
    processed_at = db.Column(db.DateTime, default=None)  # 처리된 시간
    points_awarded = db.Column(db.Integer, default=0)  # 지급된 포인트
