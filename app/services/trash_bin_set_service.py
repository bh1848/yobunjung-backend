from app import db
from app.models.trash_bin import TrashBin
from app.models.trash_bin_set import TrashBinSet

# 유효한 쓰레기 유형
VALID_TRASH_TYPES = ["paper", "plastic", "can"]

# 모든 쓰레기통 조회
def get_all_trash_bins():
    bins = TrashBinSet.query.all()
    return [
        {
            "id": bin.id,
            "latitude": bin.latitude,
            "longitude": bin.longitude,
        }
        for bin in bins
    ], 200

# 쓰레기통 상태 업데이트
def update_trash_bin_status(bin_id, status):
    trash_bin = TrashBin.query.get(bin_id)

    if not trash_bin:
        return {"msg": "쓰레기통을 찾을 수 없습니다."}, 404

    # 상태가 유효한지 확인
    if status not in ["on", "full"]:
        return {"msg": "유효하지 않은 상태입니다. 'on' 또는 'full'이어야 합니다."}, 400

    trash_bin.status = status
    db.session.commit()

    return {"msg": f"쓰레기통 {bin_id}의 상태가 '{status}'로 업데이트되었습니다."}, 200

# 쓰레기통 세트 정보 조회
def get_trash_bin_set(set_id):
    trash_bin_set = TrashBinSet.query.get(set_id)

    if not trash_bin_set:
        return {"msg": "쓰레기통 세트를 찾을 수 없습니다."}, 404

    return {
        "set_id": trash_bin_set.id,
        "address": trash_bin_set.address,
        "bins": [
            {"trash_type": bin.trash_type, "status": bin.status}  # 'trash_type'으로 수정
            for bin in trash_bin_set.bins
        ]
    }, 200

# 새로운 쓰레기통 세트 생성
def create_trash_bin_set(name, latitude, longitude, address):
    new_set = TrashBinSet(name=name, latitude=latitude, longitude=longitude, address=address)
    db.session.add(new_set)
    db.session.commit()

    # 세트에 속하는 쓰레기통 3개 추가
    for trash_type in VALID_TRASH_TYPES:
        new_bin = TrashBin(set_id=new_set.id, trash_type=trash_type)  # 'trash_type'으로 수정
        db.session.add(new_bin)

    db.session.commit()

    # 사전(dict)을 반환하고, 컨트롤러에서 jsonify로 변환
    return {"msg": "쓰레기통 세트 추가 성공", "set_id": new_set.id}, 201

# 쓰레기통 삭제
def delete_trash_bin_set(set_id):
    trash_bin_set = TrashBinSet.query.get(set_id)

    if not trash_bin_set:
        return {"msg": "해당 쓰레기통 세트를 찾을 수 없습니다."}, 404

    # 세트에 포함된 쓰레기통 모두 삭제
    TrashBin.query.filter_by(set_id=set_id).delete()

    # 세트 자체 삭제
    db.session.delete(trash_bin_set)
    db.session.commit()

    return {"msg": f"쓰레기통 세트 {set_id}이(가) 성공적으로 삭제되었습니다."}, 200
