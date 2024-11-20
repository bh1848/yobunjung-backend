import cv2
import numpy as np
from flask import request, jsonify, Response, stream_with_context

from app.services.recycle_service import (
    create_qr_code,
    update_user_points, get_event_stream, detect_objects
)


# qr 생성
def create_qr_controller(trash_type, user_id):
    """QR 코드를 생성하고, Base64로 인코딩된 QR 코드를 반환합니다."""
    if not trash_type or not user_id:
        raise ValueError("유효하지 않은 분류 정보 또는 사용자 ID입니다.")
    return create_qr_code(trash_type, user_id)


# 쓰레기 사진 인식
def handle_detection():
    """
    업로드된 이미지를 처리하고 결과를 반환합니다.
    """
    if 'image' not in request.files:
        return jsonify({"error": "이미지가 업로드되지 않았습니다."}), 400

    file = request.files['image']
    try:
        # 이미지 읽기
        image_np = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        # 감지 실행
        detections = detect_objects(image)

        # 결과 반환
        return jsonify({"trash_type": detections}), 200

    except Exception as e:
        return jsonify({"error": f"감지 오류: {str(e)}"}), 500


# 포인트 적립
def add_user_points_controller():
    """포인트 적립 요청을 처리하고 응답을 반환하는 컨트롤러"""
    data = request.get_json()
    user_id = data.get("user_id")
    trash_type = data.get("trash_type")
    trash_boolean = data.get("trash_boolean")

    # 필수 데이터가 누락된 경우 에러 반환
    if not user_id or not trash_type or trash_boolean is None:
        return jsonify({"error": "user_id, trash_type, trash_boolean을 제공해야 합니다."}), 400

    try:
        # 쓰레기 투입 여부가 참일 경우에만 포인트 적립 진행
        points_added, success_message = update_user_points(user_id, trash_type, trash_boolean)
        return jsonify({"message": success_message, "points_added": points_added}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404  # 사용자 없음
    except Exception as e:
        return jsonify({"error": "포인트 적립 중 오류 발생"}), 500  # 기타 오류


# 쓰레기 투입됐는지 확인 SSE(프론트랑 연동)
def stream_sse(user_id):
    """SSE 데이터를 스트리밍하는 컨트롤러"""
    try:
        event_stream = get_event_stream(user_id)
        return Response(stream_with_context(event_stream), content_type='text/event-stream')
    except Exception as e:
        return {"error": str(e)}, 500
