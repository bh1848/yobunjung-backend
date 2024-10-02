import cv2


def is_trash_detected(image_path):
    """
    OpenCV를 사용하여 쓰레기인지 판단하는 함수
    """
    image = cv2.imread(image_path)
    # OpenCV 기반으로 쓰레기 인식 알고리즘 추가
    # 예: 특정 물체 감지 또는 색상 분석 등
    # 여기서는 간단하게 이미지가 있으면 쓰레기라고 가정

    if image is not None:
        return True
    return False
