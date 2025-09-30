# Yobunjung Backend (분리수거 가이드 & 스마트 로그 시스템)

## 📌 프로젝트 개요
**Yobunjung**은 사용자의 분리수거 습관을 개선하기 위해 개발된 플랫폼입니다.  
AI 모델(ONNX 기반)을 활용하여 쓰레기 분류 가이드를 제공하고,  
재활용 로그를 기록하여 사용자에게 피드백을 주는 백엔드 시스템입니다.  

---

## 🛠 Tech Stack
- **Language**: Python 3
- **Framework**: Flask
- **Database**: SQLite / MySQL (환경에 따라 교체 가능)
- **AI Model**: YOLO 기반 ONNX 모델
- **API**: REST API
- **Others**: Server-Sent Events (SSE) for real-time feedback

---

## ⚙️ 아키텍처 & 주요 기능
- **Controllers**:  
  - `auth_controller` → 회원가입/로그인, 인증 처리  
  - `guide_controller` → 분리수거 가이드 제공  
  - `recycle_controller` → 재활용 로그 기록/조회  
  - `trash_bin_controller` → 쓰레기통 관리  
  - `user_controller` → 사용자 정보 관리  

- **Models**:  
  - `user.py` → 사용자 데이터 모델  
  - `recycle_log.py` → 재활용 로그 기록  
  - `trash_bin.py / trash_bin_set.py` → 쓰레기통 관리  
  - `yolo_model.py` → ONNX 기반 AI 모델 로딩 및 추론  

- **Routes**:  
  - RESTful API 라우팅 (auth, recycle, trash_bin, guide, user)  

### 주요 기능
- **회원 관리**
  - 회원가입, 로그인, 사용자 프로필 관리
- **분리수거 가이드**
  - AI 모델 기반 분류 가이드 제공
- **재활용 로그**
  - 쓰레기 배출 성공/실패 여부 기록
  - 사용자별 로그 조회
- **실시간 피드백**
  - SSE(Server-Sent Events)를 통한 분리수거 결과 알림
- **쓰레기통 관리**
  - 쓰레기통/쓰레기통 세트 등록 및 조회

---

## 👤 My Role (방혁)
- **AI 모델 연동**
  - YOLO ONNX 모델을 Flask 서버에 통합
  - 분류 결과를 API로 제공
- **재활용 로그 관리**
  - `recycle_controller`, `recycle_log` 모델 설계 및 구현
  - 쓰레기 배출 성공 여부 기록 로직 구현
- **실시간 피드백**
  - SSE(Server-Sent Events) 기반 비동기 알림 로직 구현
- **데이터베이스**
  - 사용자, 쓰레기통, 로그 모델 설계 및 CRUD API 개발
- **인증·보안**
  - 사용자 인증 처리 로직 개발 (기본 토큰 기반)
