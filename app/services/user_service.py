from app import db
from app.models.recycle_log import RecycleLog
from app.models.user import User
from sqlalchemy import func


def get_user_home_info(user_id):
    # 사용자 정보 조회
    user = User.query.get(user_id)

    if not user:
        return {"msg": "사용자를 찾을 수 없습니다."}, 404

    # 품목별 재활용 횟수 조회
    recycle_counts = db.session.query(
        RecycleLog.bin_type,
        func.sum(RecycleLog.recycle_count).label('total_recycles')
    ).filter_by(user_id=user_id).group_by(RecycleLog.bin_type).all()

    recycle_count_dict = {item.bin_type: item.total_recycles for item in recycle_counts}

    # 각 품목별 기본값 설정
    for bin_type in ["paper", "plastic", "can"]:
        if bin_type not in recycle_count_dict:
            recycle_count_dict[bin_type] = 0

    # 최근 재활용 내역 3개 조회 (시간, 품목, 얻은 포인트)
    recent_recycles = RecycleLog.query.filter_by(user_id=user_id).order_by(RecycleLog.timestamp.desc()).limit(3).all()

    # 사용자 정보, 포인트, 품목별 재활용 횟수, 최근 재활용 내역 반환
    return {
        "nickname": user.name,
        "points": user.points,  # 사용자 포인트
        "recycle_counts": recycle_count_dict,
        "recent_recycles": [
            {
                "bin_type": log.bin_type,
                "earned_points": log.earned_points,  # 얻은 포인트
                "timestamp": log.timestamp.strftime('%Y-%m-%d %H:%M:%S')  # 재활용 시간 (포맷 조정 가능)
            }
            for log in recent_recycles
        ]
    }, 200


def get_user_recycle_logs(user_id):
    # 특정 사용자의 모든 재활용 로그를 가져오기
    recycle_logs = RecycleLog.query.filter_by(user_id=user_id).all()

    # 결과를 리스트로 변환
    recycle_log_list = [
        {
            "user_id": log.user_id,
            "bin_type": log.bin_type,
            "recycle_count": log.recycle_count,
            "earned_points": log.earned_points,
            "timestamp": log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        for log in recycle_logs
    ]

    return recycle_log_list, 200

