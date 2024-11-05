from flask import request, Blueprint, jsonify

from app.services.trash_bin_service import update_trash_bin_status_by_fill_level

trash_bin_bp = Blueprint('trash_bin', __name__, url_prefix='/trash_bin')


# 쓰레기통 포화도 변경
@trash_bin_bp.route('/update_fill_level', methods=['POST'])
def update_fill_level():
    data = request.get_json()
    trash_type = data.get("trash_type")
    fill_level = data.get("fill_level")

    if trash_type is None or fill_level is None:
        return jsonify({"error": "trash_type와 fill_level이 필요합니다."}), 400

    # 서비스 함수 호출하여 상태 업데이트
    response, status_code = update_trash_bin_status_by_fill_level(trash_type, fill_level)
    return jsonify(response), status_code