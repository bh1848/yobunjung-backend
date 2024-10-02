from app import db


class TrashBin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 쓰레기통 이름 (예: 위치 설명)
    latitude = db.Column(db.Float, nullable=False)  # 위도
    longitude = db.Column(db.Float, nullable=False)  # 경도
