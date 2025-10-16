# app.py
# 텔레그램 + 네이버 뉴스 실시간 알리미 봇
# (코드는 이전 메시지에서 준 것 그대로 붙여넣기)
%%writefile app.py
import os
import re
import time
import hashlib
import html
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv()

import httpx
from apscheduler.schedulers.background import BackgroundScheduler

from sqlalchemy import create_engine, Column, Integer, String, DateTime, UniqueConstraint, Text
from sqlalchemy.orm import sessionmaker, declarative_base

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("8356788385:AAFWMEmKluIgjMec00IPgcmNOJ9RLuc9-No")
NAVER_CLIENT_ID = os.getenv("_ugeb0Ht1sXN8OCPAZdh")
NAVER_CLIENT_SECRET = os.getenv("rMmz1cisV2")

assert TELEGRAM_TOKEN, "TELEGRAM_TOKEN missing"
assert NAVER_CLIENT_ID and NAVER_CLIENT_SECRET, "NAVER client credentials missing"

# ---------- DB ----------
Base = declarative_base()
engine = create_engine("sqlite:///newsbot.db")
SessionLocal = sessionmaker(bind=engine)

class Keyword(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, index=True)
    keyword = Column(String, index=True)
    __table_args__ = (UniqueConstraint('chat_id', 'keyword', name='uq_chat_keyword'),)

class SentArticle(Base):
    __tablename__ = "sent_articles"
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, index=True)
    keyword = Column(String, index=True)
    article_hash = Column(String, index=True)  # dedup key
    title = Column(Text)
    link = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('chat_id','keyword','article_hash', name='uq_sent'),)

class ChatConfig(Base):
    __tablename__ = "chat_config"
    chat_id = Column(String, primary_key=True)
    interval_min = Column(Integer, default=10)

Base.metadata.create_all(engine)

# ---------- Helpers ----------
NAVER_NEWS_URL = "https://openapi.naver.com/v1/search/news.json"

def naver_search_news(keyword: str, display: int = 20):
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": keyword,
        "display": display,
        "start": 1,
        "sort": "date"  # 최신순
    }
    with httpx.Client(timeout=10.0) as client:
        r = client.get(NAVER_NEWS_URL, headers=headers, params=params)
        r.raise_for_status()
        return r.json().get("items", [])

def strip_html(s: str) -> str:
    s = re.sub(r"</?b>", "", s or "", flags=re.I)
    s = html.unescape(s)
    return s.strip()

def make_hash(title: str, link: str) -> str:
    return hashlib.sha256(f"{title}|{link}".encode("utf-8")).hexdigest()

async def send_article(context: ContextTypes.DEFAULT_TYPE, chat_id: int, title: str, link: str, desc: str = ""):
    msg = f"📰 <b>{html.escape(title)}</b>\n{link}"
    if desc:
        msg += f"\n\n{html.escape(desc[:300])}..."
    await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.HTML, disable_web_page_preview=False)

# ---------- Job ----------
async def poll_and_push(context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()
    try:
        keywords = session.query(Keyword).all()
        if not keywords:
            return
        by_chat = {}
        for k in keywords:
            by_chat.setdefault(k.chat_id, []).append(k.keyword)
        for chat_id, kw_list in by_chat.items():
            for kw in kw_list:
                try:
                    items = naver_search_news(kw, display=20)
                except Exception:
                    continue
                for it in items[:10]:
                    title = strip_html(it.get("title", ""))
                    link = it.get("link") or it.get("originallink") or ""
                    desc = strip_html(it.get("description", ""))

                    if not title or not link:
                        continue

                    h = make_hash(title, link)
                    exists = session.query(SentArticle).filter_by(
                        chat_id=str(chat_id), keyword=kw, article_hash=h
                    ).first()
                    if exists:
                        continue

                    try:
                        await send_article(context, int(chat_id), title, link, desc)
                    except Exception:
                        pass

                    session.add(SentArticle(
                        chat_id=str(chat_id),
                        keyword=kw,
                        article_hash=h,
                        title=title,
                        link=link,
                        sent_at=datetime.now(timezone.utc)
                    ))
                    session.commit()
                    time.sleep(0.2)
            time.sleep(0.2)
    finally:
        session.close()

# ---------- Commands ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    session = SessionLocal()
    try:
        if not session.query(ChatConfig).filter_by(chat_id=chat_id).first():
            session.add(ChatConfig(chat_id=chat_id, interval_min=10))
            session.commit()
    finally:
        session.close()
    text = (
        "안녕하세요! 네이버 뉴스 키워드 알리미입니다.\n\n"
        "명령어:\n"
        "• /add 키워드 — 키워드 등록\n"
        "• /list — 등록 키워드 보기\n"
        "• /remove 키워드 — 키워드 삭제\n"
        "• /interval 분 — 조회 주기 변경(기본 10분)\n"
        "예) /add AI 반도체, /interval 5"
    )
    await update.message.reply_text(text)

async def add_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    kw = " ".join(context.args).strip()
    if not kw:
        return await update.message.reply_text("사용법: /add 키워드")
    session = SessionLocal()
    try:
        if session.query(Keyword).filter_by(chat_id=chat_id, keyword=kw).first():
            return await update.message.reply_text(f"이미 등록된 키워드예요: “{kw}”")
        session.add(Keyword(chat_id=chat_id, keyword=kw))
        session.commit()
        await update.message.reply_text(f"✅ 등록됨: “{kw}”")
    finally:
        session.close()

async def list_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    session = SessionLocal()
    try:
        kws = [k.keyword for k in session.query(Keyword).filter_by(chat_id=chat_id)]
        if not kws:
            return await update.message.reply_text("등록된 키워드가 없습니다. /add 로 추가해보세요!")
        await update.message.reply_text("현재 키워드:\n- " + "\n- ".join(kws))
    finally:
        session.close()

async def remove_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    kw = " ".join(context.args).strip()
    if not kw:
        return await update.message.reply_text("사용법: /remove 키워드")
    session = SessionLocal()
    try:
        row = session.query(Keyword).filter_by(chat_id=chat_id, keyword=kw).first()
        if not row:
            return await update.message.reply_text(f"해당 키워드가 없습니다: “{kw}”")
        session.delete(row)
        session.commit()
        await update.message.reply_text(f"🗑️ 삭제됨: “{kw}”")
    finally:
        session.close()

async def set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text("사용법: /interval 분 (예: /interval 5)")
    minutes = max(2, int(context.args[0]))
    session = SessionLocal()
    try:
        cfg = session.query(ChatConfig).filter_by(chat_id=chat_id).first()
        if not cfg:
            cfg = ChatConfig(chat_id=chat_id, interval_min=minutes)
            session.add(cfg)
        else:
            cfg.interval_min = minutes
        session.commit()
    finally:
        session.close()
    await update.message.reply_text(f"⏱️ 조회 주기가 {minutes}분으로 설정되었습니다.")

# ---------- Scheduler wiring ----------
def build_scheduler(app):
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    def wrapper():
        app.create_task(poll_and_push(app.bot))
    scheduler.add_job(wrapper, "interval", minutes=2, id="poller", max_instances=1, coalesce=True)
    scheduler.start()
    return scheduler

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_keyword))
    app.add_handler(CommandHandler("list", list_keywords))
    app.add_handler(CommandHandler("remove", remove_keyword))
    app.add_handler(CommandHandler("interval", set_interval))
    build_scheduler(app)
    print("✅ Bot polling started. 이 셀을 계속 실행 상태로 두세요.")
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()

