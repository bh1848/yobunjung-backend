import os

from flask import Flask, jsonify
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.services.guide_service import PDFService
from config import Config

# DB, Migrate, Login Manager 초기화
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 플라스크 애플리케이션에 확장 기능 등록
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # 로그인되지 않은 경우 처리 (JSON 응답으로 처리)
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return jsonify({"message": "로그인이 필요합니다."}), 401

    # DB 모델 설정 및 초기화
    with app.app_context():
        from app.models.user import User  # 지연 임포트
        db.create_all()

    # PDF 파일 경로 지정 및 텍스트 로드 (절대 경로 사용)
    base_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 절대 경로
    pdf_path = os.path.join(base_dir, "static", "guide.pdf")

    try:
        PDFService.load_pdf_to_cache(pdf_path)
        print(f"PDF 파일에서 텍스트 로드 완료: {pdf_path}")
    except FileNotFoundError:
        print(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
    except Exception as e:
        print(f"PDF 파일 로드 중 오류 발생: {str(e)}")

    # 블루프린트 등록
    from app.routes.auth_routes import auth_bp
    from app.routes.trash_bin_set_routes import trash_bin_set_bp
    from app.routes.user_routes import user_bp
    from app.routes.recycle_routes import recycle_bp
    from app.routes.guide_routes import guide_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(trash_bin_set_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(recycle_bp)
    app.register_blueprint(guide_bp)

    return app


@login_manager.user_loader
def load_user(user_id):
    """
    사용자의 ID로부터 사용자를 로드하는 함수 (Flask-Login용).
    """
    from app.models.user import User  # 지연 임포트
    return User.query.get(int(user_id))
