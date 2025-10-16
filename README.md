# Naver News Telegram Bot — Render & Docker Package (Full Code)

## Deploy on Render (Docker auto-detected)
1) Push these files to GitHub (root)
2) Render → New → Web Service → Connect repo (Language: Docker)
3) Leave Build/Start empty (Dockerfile handles it)
4) Environment → add:
   - TELEGRAM_TOKEN
   - NAVER_CLIENT_ID
   - NAVER_CLIENT_SECRET
5) Deploy → Logs: `✅ Bot polling started.`

## Python Web Service (without Docker)
- Delete `Dockerfile`
- Build Command: `pip install -r requirements.txt`
- Start Command: `python app.py`
- Use the same environment variables
