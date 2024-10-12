from flask import Blueprint
from app.controllers.guide_controller import PDFController

# Blueprint 설정
guide_bp = Blueprint('guide', __name__, url_prefix='/guide')


# 경로 설정
@guide_bp.route('', methods=['POST'])
def ask_recycle_guide():
    return PDFController.ask_recycle_guide()
