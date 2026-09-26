"""Работа с Telegram Bot API: отправка, редактирование, кнопки, приём апдейтов."""

import os
import html
import json
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("CHAT_ID", "").strip()
BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


def api(method: str, payload: dict, timeout: int = 20):
    if not BOT_TOKEN:
        print("[tg] нет BOT_TOKEN в .env")
        return None
    try:
        r = requests.post(f"{BASE}/{method}", json=payload, timeout=timeout)
        data = r.json()
        if not data.get("ok"):
            print(f"[tg] {method}: {data}")
        return data
    except Exception as e:
        print(f"[tg] {method} исключение: {e}")
        return None


def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML",
               "disable_web_page_preview": True}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return api("sendMessage", payload)


def edit_message(chat_id, message_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text,
               "parse_mode": "HTML", "disable_web_page_preview": True}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return api("editMessageText", payload)


def answer_callback(callback_id, text=""):
    return api("answerCallbackQuery", {"callback_query_id": callback_id, "text": text})


def get_updates(offset, timeout=25):
    try:
        r = requests.get(f"{BASE}/getUpdates",
                         params={"offset": offset, "timeout": timeout},
                         timeout=timeout + 10)
        return r.json().get("result", [])
    except Exception as e:
        print(f"[tg] getUpdates исключение: {e}")
        return []


# --- форматирование вакансии ---

def vacancy_text(v: dict, header: str = "") -> str:
    tag = "🏠 удалённо" if v["remote"] else "🏢 офис/гибрид"
    body = (
        f"🆕 <b>{html.escape(v['name'])}</b>\n"
        f"🏛 {html.escape(v['employer'])}\n"
        f"💰 {html.escape(v['salary'])}\n"
        f"📍 {html.escape(v['area'])} · {tag}\n"
        f"🔎 <i>{html.escape(v['matched'])}</i>\n"
        f'👉 <a href="{v["url"]}">Открыть вакансию</a>'
    )
    return (header + "\n\n" + body) if header else body


# --- отправка уведомлений о новых (используется в main) ---

def send_text(text: str):
    if not CHAT_ID:
        print("[tg] нет CHAT_ID в .env — пропускаю отправку")
        return
    send_message(CHAT_ID, text)


def send_vacancy(v: dict):
    if not CHAT_ID:
        return
    send_message(CHAT_ID, vacancy_text(v))
