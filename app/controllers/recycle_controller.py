from flask import jsonify

from app.services.recycle_service import get_user_recycle_logs


# 현재 사용자의 재활용 내역 조회 컨트롤러
def get_user_recycle_logs_controller(user_id):
    recycle_logs, status_code = get_user_recycle_logs(user_id)
    return jsonify(recycle_logs), status_code
