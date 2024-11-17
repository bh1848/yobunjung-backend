from flask import jsonify, request
from app.services.trash_bin_set_service import (
    get_all_trash_bins,
    update_trash_bin_status,
    get_trash_bin_set,
    create_trash_bin_set, delete_trash_bin_set
)


# 모든 쓰레기통 조회 컨트롤러
def get_trash_bins_controller():
    response, status_code = get_all_trash_bins()
    return jsonify(response), status_code


# 쓰레기통 상태 업데이트 컨트롤러
def update_status_controller(bin_id):
    data = request.json
    status = data.get('status')
    response, status_code = update_trash_bin_status(bin_id, status)
    return jsonify(response), status_code


# 쓰레기통 정보 조회 컨트롤러
def get_trash_bin_set_controller(set_id):
    response, status_code = get_trash_bin_set(set_id)
    return jsonify(response), status_code


# 새로운 쓰레기통 세트 생성 컨트롤러
def create_trash_bin_set_controller():
    data = request.json
    name = data.get('name')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    address = data.get('address')

    if not all([name, latitude, longitude, address]):
        return jsonify({"msg": "필수 필드가 누락되었습니다."}), 400

    response, status_code = create_trash_bin_set(name, latitude, longitude, address)
    return jsonify(response), status_code


# 쓰레기통 세트 삭제 엔드포인트
def delete_trash_bin_set_controller(set_id):
    result, status_code = delete_trash_bin_set(set_id)
    return jsonify(result), status_code
