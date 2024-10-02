from app.models.trash_bin import TrashBin


def get_all_trash_bins():
    """
    모든 쓰레기통 위치 조회
    """
    bins = TrashBin.query.all()
    return [
        {
            "id": bin.id,
            "name": bin.name,
            "latitude": bin.latitude,
            "longitude": bin.longitude
        }
        for bin in bins
    ], 200
