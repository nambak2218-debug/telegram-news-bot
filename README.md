# Naver News Telegram Bot

텔레그램 봇을 통해 등록한 키워드 관련 최신 네이버 뉴스를 자동으로 받아보는 서비스입니다.

## 실행 방식
1. Render에서 “New Web Service” → GitHub 저장소 연결  
2. Build Command: `pip install -r requirements.txt`  
3. Start Command: `python app.py`

## 환경변수(Environment Variables)
- TELEGRAM_TOKEN = 8356788385:AAFWMEmKluIgjMec00IPgcmNOJ9RLuc9-No
- NAVER_CLIENT_ID = _ugeb0Ht1sXN8OCPAZdh
- NAVER_CLIENT_SECRET = rMmz1cisV2

## 주요 명령어
- `/start` : 봇 시작
- `/add 키워드` : 키워드 등록
- `/list` : 등록 키워드 보기
- `/remove 키워드` : 키워드 삭제
- `/interval 분` : 뉴스 조회 주기 설정

