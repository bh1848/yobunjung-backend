import cv2
import requests
from pyzbar.pyzbar import decode
from app.services.recycle_service import create_qr_code

# 아두이노 IP 주소
arduino_ip = "http://192.168.0.100"  # 아두이노의 IP 주소로 변경
send_qr_url = f"{arduino_ip}/receive_qr"  # 아두이노의 QR 데이터 수신 엔드포인트

def send_qr_to_arduino(user_id, trash_type):
    """QR 데이터를 아두이노에 HTTP POST로 전송"""
    try:
        response = requests.post(send_qr_url, json={"user_id": user_id, "trash_type": trash_type}, timeout=5)
        if response.status_code == 200:
            print("아두이노에 QR 데이터가 성공적으로 전송되었습니다.")
        else:
            print(f"전송 오류: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"아두이노에 연결할 수 없습니다: {e}")

def camera_qr_detector():
    """카메라로 QR 코드를 인식하고, 인식된 데이터를 아두이노로 전송"""
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("카메라에서 프레임을 읽을 수 없습니다.")
            break

        qr_codes = decode(frame)
        for qr_code in qr_codes:
            qr_data = qr_code.data.decode('utf-8')
            print(f"QR 코드 데이터: {qr_data}")

            try:
                user_id, trash_type = create_qr_code(qr_data)
                print(f"사용자 ID: {user_id}, 쓰레기 종류: {trash_type}")

                # 아두이노로 QR 데이터 전송
                send_qr_to_arduino(user_id, trash_type)

            except ValueError as e:
                print(f"QR 코드 데이터 처리 실패: {e}")

        cv2.imshow("QR Code Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    camera_qr_detector()