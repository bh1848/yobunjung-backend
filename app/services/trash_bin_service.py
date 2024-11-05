from app import db
from app.models.trash_bin import TrashBin


# 쓰레기통 포화도 변경
def update_trash_bin_status_by_fill_level(trash_type, fill_level):
    """
    아두이노에서 전송한 포화도에 따라 쓰레기통의 상태를 업데이트합니다.
    90% 이상이면 status를 'full'로 변경합니다.
    """
    # trash_type으로 쓰레기통 조회
    trash_bin = TrashBin.query.filter_by(trash_type=trash_type).first()

    if not trash_bin:
        return {"msg": "쓰레기통을 찾을 수 없습니다."}, 404

    # 포화도에 따라 상태 변경
    if fill_level >= 90:
        trash_bin.status = "full"
    else:
        trash_bin.status = "on"

    db.session.commit()

    return {"msg": f"쓰레기통 {trash_type}의 상태가 '{trash_bin.status}'로 업데이트되었습니다."}, 200