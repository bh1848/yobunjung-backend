# controller.py
from app.services.recycle_service import (
    create_qr_code,
    detect,
    send_bin_signal,
    update_user_points
)

def create_qr_controller(classification, user_id):
    """QR 코드를 생성하고, Base64로 인코딩된 QR 코드를 반환합니다."""
    if not classification or not user_id:
        raise ValueError("유효하지 않은 분류 정보 또는 사용자 ID입니다.")
    return create_qr_code(classification, user_id)

def detect_controller(image):
    """이미지에서 물체를 분류하고 결과를 반환합니다."""
    classification = detect(image)
    if not classification:
        raise ValueError("물체 분류 실패")
    return classification

def send_bin_signal_controller(bin_type):
    """아두이노로 분류에 맞는 신호를 전송합니다."""
    if not bin_type:
        raise ValueError("유효하지 않은 분류 정보입니다.")
    send_bin_signal(bin_type)

def update_user_points_controller(user_id, bin_type):
    """사용자 포인트를 적립하고 추가된 포인트를 반환합니다."""
    return update_user_points(user_id, bin_type)
