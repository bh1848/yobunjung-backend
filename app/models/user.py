from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # password_hash 대신 plain text 사용
    name = db.Column(db.String(80), nullable=False)
    nickname = db.Column(db.String(50), unique=True, nullable=False)

    def set_password(self, password):
        # 비밀번호를 해시하지 않고 평문 그대로 저장
        self.password = password

    def check_password(self, password):
        # 비밀번호 비교 시 평문 그대로 비교
        return self.password == password
