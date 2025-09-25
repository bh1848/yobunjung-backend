# 요분정 (Yobunjung): AI 기반 스마트 자원 순환 솔루션

## 프로젝트 개요 및 목표

\*\*요분정 (Yobunjung)\*\*은 인공지능(AI) 기반 객체 감지 및 대규모 언어 모델(LLM)을 통합하여 **분리수거의 정확성을 극대화**하고, 사용자에게 **실시간 보상과 맞춤형 가이드를 제공**하는 백엔드 API 서비스입니다.

### 핵심 목표

1.  **AI 정확성 확보:** ONNX 모델을 활용하여 다양한 쓰레기 종류를 정확하게 분류하고, 환경 데이터의 신뢰도를 높입니다.
2.  **사용자 인센티브:** 분리수거 성공 시 포인트를 즉시 지급하고, SSE(Server-Sent Events)를 통해 실시간 피드백을 제공하여 재활용 참여를 독려합니다.
3.  **통합 관제 시스템:** 스마트 쓰레기통의 위치 및 포화도 상태를 실시간으로 모니터링할 수 있는 안정적인 데이터 파이프라인을 구축합니다.

-----

## 기술 스택 및 개발 환경

| 분류 | 기술 스택 | 주요 역할 및 특징 |
| :--- | :--- | :--- |
| **웹 & 프레임워크** | Python 3.10+ / **Flask** | 경량화된 API 서버 구축 및 RESTful API 설계 |
| **데이터베이스** | **MySQL** | `PyMySQL` 드라이버를 사용한 데이터 영속성 관리 (`Flask-SQLAlchemy`, `Flask-Migrate`) |
| **AI/ML 추론** | **ONNX Runtime** | YOLO 기반 객체 감지 모델을 배포하여 고성능 추론 환경 구축 |
| **LLM 연동** | **OpenAI API (GPT-4)** | `pdfplumber`로 추출한 문서를 기반으로 재활용 Q\&A 기능 구현 (RAG 패턴) |
| **실시간 통신** | **SSE (Server-Sent Events)** | 쓰레기 투입 성공/실패 여부를 사용자에게 즉시 알림 |
| **인증** | **QR Code, Flask-Login** | 사용자 ID 기반의 QR 코드 생성 및 서버 세션 관리 |

-----

## 아키텍처 및 데이터 흐름

### 1\. 객체 감지 및 보상 파이프라인

1.  **QR 인증:** 사용자가 `/recycle/create_qr`을 호출하여 **사용자 ID**가 포함된 QR 코드를 발급받습니다.
2.  **AI 감지:** 스마트 쓰레기통 센서가 `/recycle/detect`로 **이미지**를 전송하면, 서버는 **`app/models/best.onnx`** 모델을 사용하여 쓰레기 종류를 식별합니다.
3.  **SSE 알림:** 백그라운드에서 `/recycle/<user_id>/is_successful` 엔드포인트를 구독하는 사용자에게 감지 성공/실패 여부를 **실시간 스트리밍**합니다.
4.  **포인트 지급:** 감지 성공 시 `/recycle/add_points`를 통해 DB의 `User` 테이블과 `RecycleLog` 테이블을 업데이트합니다.

### 2\. PDF 가이드 Q\&A (RAG)

1.  **문서 캐싱:** 앱 시작 시 `app/__init__.py`에서 \*\*`app/static/guide.pdf`\*\*의 내용을 추출하여 `PDFService`에 메모리 캐싱합니다.
2.  **질문 요청:** 사용자가 `/guide` 엔드포인트에 질문을 요청합니다.
3.  **LLM 호출:** 캐시된 문서의 내용과 사용자의 질문을 조합하여 **OpenAI API**에 전송하고, 정확하고 근거 있는 답변을 받아 사용자에게 반환합니다.

-----

## 로컬 환경 설정 및 실행 방법

### 1\. 프로젝트 설정

```bash
# 1. GitHub 리포지토리 클론
git clone [YOUR_REPOSITORY_URL]
cd yobunjung

# 2. Python 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # macOS/Linux 환경

# 3. 의존성 설치
pip install -r requirements.txt
```

### 2\. 데이터베이스 및 환경 변수 설정

`config.py` 파일 또는 환경 변수를 설정합니다.

```python
# config.py (예시)
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_for_yobunjung')
    # MySQL DB 설정 (환경에 맞게 반드시 변경)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://yobunjung:1234@localhost/yobunjung_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # OpenAI API Key는 환경 변수 또는 config 파일에서 관리
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
```

### 3\. 데이터베이스 초기화 (마이그레이션)

```bash
# Flask 애플리케이션 지정
export FLASK_APP=app

# 데이터베이스 스키마 적용
flask db init      # 최초 1회 실행
flask db migrate -m "Initial schema setup for Yobunjung"
flask db upgrade
```

### 4\. 필수 리소스 파일 준비

코드가 참조하는 3가지 핵심 파일을 반드시 해당 경로에 배치해야 합니다.

  * `app/models/best.onnx`
  * `app/static/guide.pdf`
  * `app/static/logo.png`

### 5\. 서버 실행

```bash
flask run
# 서버가 http://127.0.0.1:5000/ 에서 실행됩니다.
```

-----

## 주요 API 엔드포인트 레퍼런스

| 기능 | HTTP 메서드 | 엔드포인트 | 요청 JSON Body (예시) | 응답 (주요 데이터) |
| :--- | :--- | :--- | :--- | :--- |
| **회원가입** | `POST` | `/auth/register` | `{"email": "...", "password": "...", "name": "..."}` | `{"message": "회원가입 성공"}` |
| **QR 생성** | `POST` | `/recycle/create_qr` | `{"trash_type": "Plastic", "user_id": 1}` | `{"qr_code": "Base64 이미지 데이터"}` |
| **AI 감지** | `POST` | `/recycle/detect` | `multipart/form-data` (쓰레기 이미지) | `{"result": "Can", "log_id": 123}` |
| **실시간 알림** | `GET` | `/recycle/1/is_successful` | - | SSE Data: `{"is_successful": true, "points": 100}` |
| **가이드 Q\&A** | `POST` | `/guide` | `{"question": "이물질 묻은 비닐은 어떻게 버리나요?"}` | `{"answer": "..."}` |
| **쓰레기통 상태** | `POST` | `/trash_bin/update_fill_level` | `{"trash_type": "Paper", "fill_level": 95}` | `{"message": "상태 업데이트 완료"}` |
| **내 정보 조회** | `GET` | `/user/1/home` | - | `{"name": "...", "points": 500}` |

-----

### 기술적 성과

  * **컴포넌트 분리 (MVC/Layered Architecture):** `routes`, `controllers`, `services`, `models`로 계층을 명확히 분리하여 높은 유지보수성과 확장성을 확보했습니다.
  * **비동기 처리 (SSE):** 장시간 연결이 필요한 알림 기능을 **SSE**를 통해 효율적으로 구현하여 사용자 경험을 개선했습니다.
  * **ORM 활용:** Flask-SQLAlchemy와 Flask-Migrate를 사용하여 안전하고 버전 관리 가능한 데이터베이스 스키마 관리를 실현했습니다.
