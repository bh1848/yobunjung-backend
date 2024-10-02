from app import db


class TrashBinSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)  # 세트의 위치 (위도)
    longitude = db.Column(db.Float, nullable=False)  # 세트의 위치 (경도)
    address = db.Column(db.String(255), nullable=False)  # 주소 추가
    name = db.Column(db.String(100), nullable=False)  # 세트 이름
