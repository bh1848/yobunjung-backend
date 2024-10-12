from flask import jsonify, request
from app.services.guide_service import GPTService


class PDFController:
    @staticmethod
    def ask_recycle_guide():
        """
        사용자의 질문을 받아 미리 저장된 PDF 파일을 기준으로 답변을 반환.
        품목 이름만 질문으로 들어옴.
        """
        # JSON 데이터에서 question 값 받기
        data = request.get_json()

        if not data or "question" not in data:
            return jsonify({"error": "질문을 JSON 형식으로 제출하세요."}), 400

        item_name = data["question"]  # 품목 이름
        role = data.get("role", "쓰레기 처리 전문가")  # 기본 역할 설정

        try:
            # 품목에 대한 정보 생성
            answer = GPTService.handle_item_question(item_name, role)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        return jsonify({"question": item_name, "role": role, "answer": answer})
