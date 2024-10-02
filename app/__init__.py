from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # 블루프린트 등록
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.trash_routes import trash_bp
    app.register_blueprint(trash_bp)

    from app.routes.trash_bin_routes import trash_bin_bp
    app.register_blueprint(trash_bin_bp)

    return app
