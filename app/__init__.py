from flask import Flask, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker

from app.services.guide_service import PDFService
from config import Config

# 초기화
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
Session = None  # 글로벌 변수로 선언

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # 플라스크 애플리케이션에 확장 기능 등록
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # PDF 파일 경로를 Config에서 가져옴 (예: 'static/myfile.pdf')
    pdf_path = app.config.get("PDF_PATH", "app/static/guide.pdf")

    # PDF 파일 로드
    try:
        PDFService.load_pdf_to_cache(pdf_path)
    except FileNotFoundError as e:
        print(f"PDF 로드 실패: {e}")

    # 로그인되지 않은 경우 처리 (JSON 응답으로 처리)
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return jsonify({"message": "로그인이 필요합니다."}), 401

    # 애플리케이션 컨텍스트 내에서 Session 초기화
    global Session
    with app.app_context():
        from app.models.user import User  # 필요한 모델 임포트
        db.create_all()
        Session = scoped_session(sessionmaker(bind=db.engine))

    # 블루프린트 등록
    from app.routes.auth_route import auth_bp
    from app.routes.trash_bin_set_route import trash_bin_set_bp
    from app.routes.user_route import user_bp
    from app.routes.recycle_route import recycle_bp
    from app.routes.guide_route import guide_bp
    from app.routes.trash_bin_route import trash_bin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(trash_bin_set_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(recycle_bp)
    app.register_blueprint(guide_bp)
    app.register_blueprint(trash_bin_bp)

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))
