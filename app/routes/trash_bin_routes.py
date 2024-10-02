from flask import Blueprint

from app.controllers.trash_bin_controller import (
    update_status_controller,
    get_trash_bins_controller,
    create_trash_bin_set_controller, delete_trash_bin_set_controller
)

# Blueprint 생성
trash_bin_set_bp = Blueprint('trash_bin_set', __name__, url_prefix='/trash_bin_set')


# 모든 쓰레기통 위치 조회
@trash_bin_set_bp.route('', methods=['GET'])
def get_trash_bin_set_route():
    return get_trash_bins_controller()


# 쓰레기통 상태 업데이트
@trash_bin_set_bp.route('/<int:bin_id>/update', methods=['POST'])
def update_status_route(bin_id):
    return update_status_controller(bin_id)


# 쓰레기통 상태 조회
@trash_bin_set_bp.route('/<int:bin_id>', methods=['GET'])
def get_trash_bin_set_status_route():
    return get_trash_bins_controller()  # get_status 함수 호출을 추가


# 새로운 쓰레기통 세트 추가
@trash_bin_set_bp.route('', methods=['POST'])
def add_trash_bin_set_route():
    return create_trash_bin_set_controller()  # 컨트롤러에서 데이터를 추출하도록 함


# 쓰레기통 세트 삭제 라우트
@trash_bin_set_bp.route('/<int:set_id>', methods=['DELETE'])
def delete_trash_bin_set_route(set_id):
    return delete_trash_bin_set_controller(set_id)