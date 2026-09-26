# Job-hunter 🕵️ — вакансии в Telegram

Бот поллит **hh.ru** и присылает тебе в Telegram каждую **новую** вакансию по твоим фильтрам
(junior / стажировки / без опыта, Россия + удалёнка). Без спама: при первом запуске текущие
вакансии молча заносятся в базу, дальше приходят только свежие.

## Как запустить (5 минут)

1. **Создай бота** — напиши [@BotFather](https://t.me/BotFather) → `/newbot` → получи `BOT_TOKEN`.
2. **Узнай свой chat_id** — напиши [@userinfobot](https://t.me/userinfobot) → `/start` → скопируй число.
3. **Настрой .env**:
   ```
   copy .env.example .env      # Windows
   ```
   и впиши `BOT_TOKEN` и `CHAT_ID`.
4. **Установи зависимости и запусти**:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python main.py --once       # тестовый прогон: должно прийти "Job-hunter запущен"
   python main.py              # рабочий режим: проверка каждые 15 минут
   ```

> ⚠️ hh.ru блокирует запросы из дата-центров/облаков — запускай **на своём компьютере**
> (домашний IP), тогда API отвечает нормально.

## Настройка под себя — `config.py`
- `SEARCHES` — список поисковых запросов (добавляй/убирай профессии).
- `AREA` — регион: `113` Россия, `1` Москва, `2` Питер, `1620` Рязань.
- `EXPERIENCE` — `noExperience` (без опыта), `between1And3` и т.д.
- `INCLUDE_REMOTE` — добавлять ли отдельно удалёнку.
- `POLL_INTERVAL_MINUTES` — как часто проверять.
- `TITLE_BLOCKLIST` — слова в названии, по которым вакансия пропускается (senior/lead и т.п.).

## Чтобы работал 24/7 (позже)
- Простой вариант: держать `python main.py` запущенным (или через `nssm`/автозагрузку).
- Или задеплоить на **Amvera** (твой PaaS) как воркер.
- Или `python main.py --once` по расписанию (Планировщик задач Windows / GitHub Actions cron).

## Структура
```
config.py     — что и где искать
hh.py         — источник вакансий (hh.ru API)
storage.py    — база уже увиденных (SQLite)
notifier.py   — отправка в Telegram
main.py       — цикл поллинга
```
