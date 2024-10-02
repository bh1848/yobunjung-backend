from flask import Blueprint, request
from app.controllers.trash_bin_controller import get_trash_bins_controller

trash_bin_bp = Blueprint('trash_bin', __name__, url_prefix='/trash_bins')


# 모든 쓰레기통 위치 조회
@trash_bin_bp.route('', methods=['GET'])
def get_trash_bins():
    return get_trash_bins_controller()
