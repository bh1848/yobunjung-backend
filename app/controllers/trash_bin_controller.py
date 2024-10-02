from flask import jsonify
from app.services.trash_bin_service import get_all_trash_bins


def get_trash_bins_controller():
    """
    쓰레기통 위치를 조회하는 컨트롤러
    """
    return jsonify(get_all_trash_bins())
