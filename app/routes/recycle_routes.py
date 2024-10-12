from flask import Blueprint
from app.controllers.recycle_controller import get_user_recycle_logs_controller

recycle_bp = Blueprint('recycle', __name__, url_prefix='/recycle')


@recycle_bp.route('/<int:user_id>/logs', methods=['GET'])
def get_user_recycle_logs_route(user_id):
    return get_user_recycle_logs_controller(user_id)