# Naver News Telegram Bot (Render-ready)

텔레그램 봇으로 등록한 키워드의 최신 네이버 뉴스를 자동 알림합니다.

## 배포 요약 (Render, Free Plan)
1) 이 리포지토리를 GitHub에 업로드  
2) Render → New + → Web Service → GitHub 연결  
3) Build Command: `pip install -r requirements.txt`  
4) Start Command: `python app.py`  
5) Environment Variables:
   - TELEGRAM_TOKEN (BotFather 토큰)
   - NAVER_CLIENT_ID (네이버 Client ID)
   - NAVER_CLIENT_SECRET (네이버 Secret)

### Docker로 배포하고 싶다면
- Render에서 "Docker" 옵션 선택 시, 이 리포의 Dockerfile을 사용해 빌드됩니다.

## 봇 명령어
- `/start` — 시작 안내
- `/add 키워드` — 키워드 등록
- `/list` — 키워드 목록
- `/remove 키워드` — 삭제
- `/interval 분` — 조회 주기 변경(기본 10분)

## 주의
- Dockerfile은 **리포지토리 루트**에 있어야 합니다. (대소문자 정확히: `Dockerfile`)
- 하위 폴더에 두는 경우 Render의 "Root Directory"를 해당 폴더로 지정하세요.
