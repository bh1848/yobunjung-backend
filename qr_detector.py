import cv2
from pyzbar.pyzbar import decode
from app.services.recycle_service import process_qr_data, send_bin_signal, update_user_points, arduino

# 포인트 적립 API URL
POINTS_API_URL = 'http://localhost:5000/recycle/update_points'


# 초음파 센서 모니터링 및 포인트 적립 요청
def monitor_trash_and_update_points(user_id, bin_type):
    """아두이노 센서 감지를 통해 포인트 적립을 트리거합니다."""
    while arduino and arduino.in_waiting > 0:
        data = arduino.readline().decode().strip()
        if data == "TRASH_DETECTED":
            points_to_add = update_user_points(user_id, bin_type)
            print(f"포인트가 성공적으로 적립되었습니다: {points_to_add}")
            break


# 카메라 QR 코드 감지 및 아두이노 제어
def camera_qr_detector():
    """카메라로 QR 코드를 인식하고, 분류에 따라 아두이노 신호를 전송합니다."""
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("카메라에서 프레임을 읽을 수 없습니다.")
            break

        # QR 코드 감지
        qr_codes = decode(frame)
        for qr_code in qr_codes:
            qr_data = qr_code.data.decode('utf-8')
            print(f"QR 코드 데이터: {qr_data}")

            try:
                # QR 코드에서 사용자 ID와 분류 정보 추출
                user_id, bin_type = process_qr_data(qr_data)
                print(f"사용자 ID: {user_id}, 분류: {bin_type}")

                # 아두이노로 신호 전송
                send_bin_signal(bin_type)

                # 초음파 센서 모니터링 및 포인트 적립 요청
                monitor_trash_and_update_points(user_id, bin_type)

            except ValueError as e:
                print(f"QR 코드 데이터 처리 실패: {e}")

        # 카메라 창에 프레임 표시
        cv2.imshow("QR Code Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    camera_qr_detector()
