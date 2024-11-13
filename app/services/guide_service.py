import os
import openai
import pdfplumber
import re

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
                text = "".join(page.extract_text() or "" for page in pdf.pages)
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

    @staticmethod
    def extract_relevant_text(keyword, text, context_length=800):
        """
        PDF 텍스트에서 주어진 키워드와 관련된 텍스트 부분을 추출.
        context_length: 키워드 주변에서 추출할 문자 수.
        """
        pattern = re.compile(rf"(.{{0,{context_length}}}{keyword}.{{0,{context_length}}})", re.IGNORECASE)
        matches = pattern.findall(text)

        if matches:
            return "\n\n".join(matches)
        else:
            return None  # 관련 텍스트가 없는 경우


class GPTService:
    @staticmethod
    def is_valid_item_name(question):
        """
        GPT에게 질문이 사물인지 판별하도록 요청하고, 사람이름이나 추상 개념이 아닌지 확인.
        """
        prompt = (
            f"'{question}'는 물리적인 사물의 이름인가요? "
            "사람 이름이나 추상적인 개념이 아닌 경우에만 '예'로 답해주세요. "
            "예/아니요 형식으로만 답해주세요."
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 사물 이름을 판별하는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=5,
            temperature=0.0,
        )

        # GPT의 응답을 확인하여 '예'인 경우에만 True를 반환
        answer = response['choices'][0]['message']['content'].strip()
        return answer.lower() == "예"

    @staticmethod
    def ask_gpt_with_role(question, context_text=None, role="쓰레기 처리 전문가"):
        """
        GPT에게 역할을 부여하고 질문에 대한 답변을 생성.
        """
        prompt = f"'{question}'의 재활용 방법을 알려주세요."
        if context_text:
            prompt += f"\n\nPDF 내용:\n{context_text}"

        messages = [
            {"role": "system", "content": f"당신은 {role}입니다."},
            {"role": "user", "content": prompt}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            temperature=0.5,
        )
        return response['choices'][0]['message']['content'].strip()

    @staticmethod
    def handle_item_question(question, role="쓰레기 처리 전문가"):
        """
        미리 저장된 PDF 텍스트를 기반으로 질문을 처리하고 답변 생성.
        """
        # 사물 유효성 검사
        if not GPTService.is_valid_item_name(question):
            return "올바르지 않은 검색어입니다. 사물 이름을 입력해주세요."

        # 1. 캐시된 PDF 텍스트 가져오기
        try:
            pdf_text = PDFService.get_pdf_text()
        except ValueError:
            return "PDF 내용을 로드하지 못했습니다."

        # 2. 관련 텍스트 추출
        relevant_text = PDFService.extract_relevant_text(question, pdf_text)
        if not relevant_text:
            return "해당 항목에 대한 정보를 PDF에서 찾을 수 없습니다."

        # 3. 추출된 텍스트로 GPT에 질문
        answer = GPTService.ask_gpt_with_role(question, relevant_text, role)

        return answer