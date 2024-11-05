from app import db


class TrashBin(db.Model):
    set_id = db.Column(db.Integer, db.ForeignKey('trash_bin_set.id'), nullable=False)  # 세트 id
    id = db.Column(db.Integer, primary_key=True)
    trash_type = db.Column(db.String(20), nullable=False)  # 쓰레기통 종류 (paper, plastic, can)
    status = db.Column(db.String(20), nullable=False, default="on")  # 상태 (on, full)
    set = db.relationship('TrashBinSet', backref=db.backref('bins', lazy=True))  # 세트와 연결
