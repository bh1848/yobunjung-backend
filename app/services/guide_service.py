import os

import openai
import pdfplumber

# OpenAI API 키를 하드코딩으로 설정 (보안 위험이 있을 수 있음)
openai.api_key = "sk-he18d8Yo7oZDvNOMJpcV3XQccF6TbhE1JtLcgi4MkgT3BlbkFJfHtsYco8T_RY_OfJ-qo_zKZv_PxxVxnJreYRNP3-sA"


class PDFService:
    pdf_text_cache = None  # PDF 텍스트를 메모리에 저장

    @staticmethod
    def load_pdf_to_cache(pdf_path):
        """
        서버 시작 시 PDF 파일을 읽어 텍스트를 캐시에 저장.
        """
        if os.path.exists(pdf_path):
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
            PDFService.pdf_text_cache = text.strip()  # 캐시에 텍스트 저장
        else:
            raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")

    @staticmethod
    def get_pdf_text():
        """
        캐시에 저장된 PDF 텍스트 반환.
        """
        if PDFService.pdf_text_cache:
            return PDFService.pdf_text_cache
        else:
            raise ValueError("PDF 텍스트가 로드되지 않았습니다.")


class GPTService:
    @staticmethod
    def ask_gpt_with_role(question, context_text, role="쓰레기 처리 전문가"):
        """
        GPT에게 역할을 부여하고 질문에 대한 답변을 생성.
        """
        prompt = (
            f"'{question}'의 재활용 방법을 알려주세요.\n\nPDF 내용:\n{context_text}"
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # GPT-3.5 모델 호출
            messages=[
                {"role": "system", "content": "당신은 쓰레기 처리 전문가입니다."},
                {"role": "user", "content": f"'{question}'의 재활용 방법을 알려주세요.\n\nPDF 내용:\n{context_text}"}
            ],
            max_tokens=600,
            temperature=0.5,
        )
        return response['choices'][0]['message']['content'].strip()

    @staticmethod
    def handle_item_question(question, role="쓰레기 처리 전문가"):
        """
        미리 저장된 PDF 텍스트를 기반으로 질문을 처리하고 답변 생성.
        """
        # 1. 캐시된 PDF 텍스트 가져오기
        try:
            pdf_text = PDFService.get_pdf_text()
        except ValueError:
            return "PDF 내용을 로드하지 못했습니다."

        # 2. 품목 이름을 기반으로 검색
        if question in pdf_text:
            answer = GPTService.ask_gpt_with_role(question, pdf_text, role)
        else:
            answer = "해당 품목에 대한 정보가 없습니다."

        return answer
