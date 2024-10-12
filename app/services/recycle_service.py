from app.models.recycle_log import RecycleLog


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

