"""Отправка уведомлений в Telegram через Bot API (sendMessage)."""

import os
import html
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("CHAT_ID", "").strip()


def _api(method: str):
    return f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"


def send_text(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("[tg] нет BOT_TOKEN/CHAT_ID в .env — пропускаю отправку")
        return
    try:
        r = requests.post(_api("sendMessage"), json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }, timeout=20)
        if not r.ok:
            print(f"[tg] ошибка: {r.status_code} {r.text}")
    except Exception as e:
        print(f"[tg] исключение: {e}")


def send_vacancy(v: dict):
    tag = "🏠 удалённо" if v["remote"] else "🏢 офис/гибрид"
    name = html.escape(v["name"])
    emp = html.escape(v["employer"])
    text = (
        f"🆕 <b>{name}</b>\n"
        f"🏛 {emp}\n"
        f"💰 {html.escape(v['salary'])}\n"
        f"📍 {html.escape(v['area'])} · {tag}\n"
        f"🔎 по запросу: <i>{html.escape(v['matched'])}</i>\n"
        f'👉 <a href="{v["url"]}">Открыть вакансию на hh.ru</a>'
    )
    send_text(text)
