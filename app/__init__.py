from flask import Flask, jsonify
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # 로그인되지 않은 경우 리디렉션 대신 JSON 응답 반환
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return jsonify({"message": "로그인이 필요합니다."}), 401

    with app.app_context():
        from app.models.user import User  # 지연 임포트
        db.create_all()

    # 블루프린트 등록
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.trash_routes import trash_bp
    app.register_blueprint(trash_bp)

    from app.routes.trash_bin_routes import trash_bin_set_bp
    app.register_blueprint(trash_bin_set_bp)

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User  # 지연 임포트
    return User.query.get(int(user_id))