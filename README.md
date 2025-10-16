# Render Fix Pack — Naver News Telegram Bot

의존성 충돌(ResolutionImpossible)을 피하기 위해 버전을 고정한 패키지 묶음입니다.

## Render (Python Web Service)로 배포
1) GitHub에 이 4개 파일을 업로드
2) Render → New Web Service → GitHub 연결
3) Build Command: `pip install -r requirements.txt`
4) Start Command: `python app.py`
5) Environment Variables 추가:
   - TELEGRAM_TOKEN
   - NAVER_CLIENT_ID
   - NAVER_CLIENT_SECRET
6) 재배포 시에는 Settings → Clear build cache 후 Deploy

## Docker 대안
- Render에서 Docker 서비스로 생성 시, 본 `Dockerfile` 사용.
