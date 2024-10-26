from flask import Blueprint
from app.controllers.guide_controller import PDFController

guide_bp = Blueprint('guide', __name__, url_prefix='/guide')


# 재활용 가이드 요청
@guide_bp.route('', methods=['POST'])
def ask_recycle_guide():
    return PDFController.ask_recycle_guide()
