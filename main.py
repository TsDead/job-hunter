"""Бот-охотник за вакансиями.

- Присылает НОВЫЕ вакансии (hh.ru РФ + RemoteOK) по мере появления.
- Команда /list — показать ТЕКУЩИЕ вакансии и листать их кнопками ◀ ▶.

Запуск:
    python main.py           # рабочий режим (long-polling + периодические уведомления)
    python main.py --once    # один цикл проверки новых и выход (для теста/cron)
"""

import sys
import time

import config
import hh
import remoteok
import remotive
import jobicy
import weworkremotely
import workingnomads
import himalayas
import habr
import getmatch
import ai_filter
import storage
import notifier

# состояние листания: chat_id -> {"items": [...], "idx": int}
STATE = {}


def collect() -> list:
    """Собрать вакансии из всех источников, убрать дубли по id."""
    vacancies = []
    if getattr(config, "HH_ENABLED", False):
        vacancies += hh.fetch()
    vacancies += remoteok.fetch()
    vacancies += remotive.fetch()
    vacancies += jobicy.fetch()
    vacancies += weworkremotely.fetch()
    vacancies += workingnomads.fetch()
    vacancies += himalayas.fetch()
    if getattr(config, "HABR_ENABLED", False):
        vacancies += habr.fetch()
    if getattr(config, "GETMATCH_ENABLED", False):
        vacancies += getmatch.fetch()
    uniq = {}
    for v in vacancies:
        uniq[v["id"]] = v
    return list(uniq.values())


# ---------- уведомления о новых ----------

def run_once(first_run: bool) -> int:
    vacancies = collect()
    new = [v for v in vacancies if storage.is_new(v["id"])]
    if first_run:
        for v in new:
            storage.mark(v["id"])
        notifier.send_text(
            f"🤖 <b>Job-hunter запущен.</b>\n"
            f"Слежу за вакансиями: 6 зарубежных бордов + РФ (Хабр Карьера, getmatch).\n"
            f"Сейчас в базе {len(new)} — дальше пришлю только <b>новые</b>.\n\n"
            f"Команда <b>/list</b> — посмотреть текущие вакансии и полистать их."
        )
        return 0
    sent = 0
    for v in reversed(new):
        s = ai_filter.score(v) if config.AI_FILTER_ENABLED else None
        storage.mark(v["id"])
        # отсеиваем неподходящие (только если оценка получена и ниже порога)
        if s and s.get("fit_score", 0) < config.FIT_THRESHOLD:
            continue
        notifier.send_message(notifier.CHAT_ID, _scored_text(v, s))
        sent += 1
        time.sleep(0.5)
    return sent


def _scored_text(v: dict, s) -> str:
    text = notifier.vacancy_text(v)
    if not s:
        return text
    emoji = {"apply": "🟢", "maybe": "🟡", "skip": "🔴"}.get(s.get("verdict"), "⚪")
    text += f"\n\n🤖 <b>AI-оценка: {s.get('fit_score')}/100 · {emoji} {s.get('verdict')}</b>"
    if s.get("seniority"):
        text += f" · уровень: {s['seniority']}"
    if s.get("summary"):
        text += f"\n\n📄 <b>Суть:</b> {s['summary']}"
    if s.get("key_requirements"):
        text += f"\n📌 <b>Требуют:</b> {', '.join(s['key_requirements'][:4])}"
    if s.get("matched_skills"):
        text += f"\n✅ <b>Совпало:</b> {', '.join(s['matched_skills'][:5])}"
    if s.get("missing_skills"):
        text += f"\n➕ <b>Подтянуть:</b> {', '.join(s['missing_skills'][:5])}"
    if s.get("salary_comment") and s["salary_comment"] != "не указана":
        text += f"\n💰 {s['salary_comment']}"
    if s.get("how_to_apply"):
        text += f"\n🎯 <b>В отклике:</b> {s['how_to_apply']}"
    if s.get("growth"):
        text += f"\n📈 <b>Рост:</b> {s['growth']}"
    if s.get("reason"):
        text += f"\n💬 {s['reason']}"
    if s.get("red_flags"):
        text += f"\n🚩 <b>Флаги:</b> {'; '.join(s['red_flags'][:4])}"
    return text


# ---------- листание /list ----------

def keyboard(idx: int, total: int) -> dict:
    return {"inline_keyboard": [
        [
            {"text": "⬅️ Назад", "callback_data": "prev"},
            {"text": f"{idx + 1}/{total}", "callback_data": "noop"},
            {"text": "Вперёд ➡️", "callback_data": "next"},
        ],
        [{"text": "🔄 Обновить список", "callback_data": "refresh"}],
    ]}


def _page_text(items, idx):
    return notifier.vacancy_text(items[idx], header=f"📋 Вакансия {idx + 1} из {len(items)}")


def cmd_list(chat_id):
    loading = notifier.send_message(chat_id, "🔎 Загружаю актуальные вакансии…")
    mid = loading and loading.get("result", {}).get("message_id")
    items = collect()
    if not items:
        notifier.edit_message(chat_id, mid, "Ничего не нашёл. Попробуй позже или измени config.py.")
        return
    STATE[chat_id] = {"items": items, "idx": 0}
    notifier.edit_message(chat_id, mid, _page_text(items, 0), keyboard(0, len(items)))


def on_callback(cq):
    data = cq.get("data", "")
    cid = cq["id"]
    msg = cq.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    mid = msg.get("message_id")
    st = STATE.get(chat_id)

    if data == "noop":
        notifier.answer_callback(cid)
        return
    if not st:
        notifier.answer_callback(cid, "Список устарел — отправь /list заново")
        return

    if data == "refresh":
        notifier.answer_callback(cid, "Обновляю…")
        items = collect()
        if not items:
            notifier.edit_message(chat_id, mid, "Ничего не нашёл сейчас.")
            return
        st["items"], st["idx"] = items, 0
    elif data == "next":
        st["idx"] = (st["idx"] + 1) % len(st["items"])
        notifier.answer_callback(cid)
    elif data == "prev":
        st["idx"] = (st["idx"] - 1) % len(st["items"])
        notifier.answer_callback(cid)
    else:
        notifier.answer_callback(cid)
        return

    notifier.edit_message(chat_id, mid, _page_text(st["items"], st["idx"]),
                          keyboard(st["idx"], len(st["items"])))


HELP = (
    "🤖 <b>Job-hunter</b> — бот Стёпы (AI / LLM Engineer)\n\n"
    "• Я сам присылаю <b>новые</b> вакансии по России и удалёнку.\n"
    "• Каждую оцениваю нейросетью: подходит или нет.\n"
    "• <b>/list</b> — показать <b>текущие</b> вакансии, листать кнопками ◀ ▶.\n"
    "• <b>/help</b> — эта справка.\n\n"
    "👨‍💻 Портфолио автора: <b>new-coder.ru</b> — AI-агенты, RAG, MCP, evaluation."
)


def on_message(m):
    text = (m.get("text") or "").strip().lower()
    chat_id = m.get("chat", {}).get("id")
    if text in ("/list", "/jobs", "list", "вакансии"):
        cmd_list(chat_id)
    elif text in ("/start", "/help", "start", "help"):
        notifier.send_message(chat_id, HELP)


def drain_offset() -> int:
    """Пропустить старые апдесты, накопившиеся пока бот был выключен."""
    ups = notifier.get_updates(0, 0)
    return ups[-1]["update_id"] + 1 if ups else 0


# ---------- главный цикл ----------

def main():
    if "--once" in sys.argv:
        first_run = storage.count() == 0
        sent = run_once(first_run)
        print(f"once: отправлено новых {sent}")
        return

    first_run = storage.count() == 0
    if first_run:
        print("Первый запуск — заношу текущие вакансии без спама.")
    run_once(first_run)

    offset = drain_offset()
    last_notify = time.time()
    interval = config.POLL_INTERVAL_MINUTES * 60
    print("Бот запущен: слушаю команды (/list) и слежу за новыми вакансиями.")

    while True:
        try:
            for u in notifier.get_updates(offset, 25):
                offset = u["update_id"] + 1
                if "message" in u:
                    on_message(u["message"])
                elif "callback_query" in u:
                    on_callback(u["callback_query"])
        except Exception as e:
            print(f"[loop] апдейты: {e}")

        if time.time() - last_notify >= interval:
            try:
                sent = run_once(False)
                print(f"[{time.strftime('%H:%M:%S')}] новых отправлено: {sent}")
            except Exception as e:
                print(f"[loop] проверка новых: {e}")
            last_notify = time.time()


if __name__ == "__main__":
    main()
