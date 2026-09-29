"""Настройки бота-охотника за вакансиями.
Правь этот файл под себя — поисковые запросы, регион, частоту проверки."""

import re as _re


def strip_html(s, limit: int = 700) -> str:
    """Убрать HTML-теги и лишние пробелы из описания вакансии, обрезать до limit."""
    if not s:
        return ""
    s = _re.sub(r"<[^>]+>", " ", str(s))
    s = (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
          .replace("&nbsp;", " ").replace("&quot;", '"').replace("&#39;", "'"))
    s = _re.sub(r"\s+", " ", s).strip()
    return s[:limit]

# --- Что искать (список текстовых запросов к hh.ru) ---
# Под 17 лет / старт: junior, стажировки, без опыта.
SEARCHES = [
    "Python junior",
    "Python стажер",
    "Python разработчик",
    "FastAPI",
    "Django junior",
    "backend junior",
    "AI",
    "machine learning junior",
    "data analyst junior",
    "QA junior",
]

# --- hh.ru ВЫКЛЮЧЕН ---
# hh.ru отдаёт 403 (анти-бот WAF) даже с браузерными заголовками и cookies —
# режет IP на корню, токен не помогает. Работаем по международной удалёнке.
# Чтобы вернуть hh: HH_ENABLED = True и запускать с сети, которую hh не банит.
HH_ENABLED = False

# --- Фильтры hh.ru (действуют, только если HH_ENABLED = True) ---
AREA = 113            # 113 = Россия. (1 = Москва, 2 = Санкт-Петербург, 1620 = Рязань)
EXPERIENCE = "noExperience"   # без опыта. Варианты: noExperience, between1And3, between3And6
PERIOD_DAYS = 1       # искать вакансии за последние N дней (для поллинга хватает 1)
PER_PAGE = 50         # сколько тянуть за запрос (макс 100)

# Включить удалёнку отдельными запросами (schedule=remote) в дополнение к обычным
INCLUDE_REMOTE = True

# --- Второй источник: RemoteOK (международная удалёнка, вакансии на английском) ---
REMOTEOK_ENABLED = True
# По каким ключам оставлять вакансии RemoteOK (ищутся в названии и тегах):
REMOTEOK_KEYWORDS = [
    "python", "django", "fastapi", "backend", "back-end", "back end",
    "ai", "machine learning", "ml", "llm", "nlp",
    "data", "junior", "internship", "qa",
    "developer", "software engineer", "full stack", "full-stack",
    "typescript", "react",
    # русские (для Хабр Карьеры и getmatch)
    "разработчик", "питон", "бэкенд", "аналитик", "данны", "стажёр", "стажер",
    "джуниор", "тестировщик", "программист", "инженер",
]

# --- Третий источник: Remotive (международная удалёнка, публичный API без ключа) ---
REMOTIVE_ENABLED = True

# --- Четвёртый источник: Jobicy (международная remote-борда, публичный JSON API) ---
JOBICY_ENABLED = True

# --- Пятый источник: We Work Remotely (крупная remote-tech борда, RSS-ленты) ---
WWR_ENABLED = True

# --- Шестой источник: Working Nomads (международная remote-борда, публичный JSON API) ---
WORKINGNOMADS_ENABLED = True

# --- Седьмой источник: Himalayas (международная remote-борда, публичный JSON API) ---
HIMALAYAS_ENABLED = True

# --- РФ-источники (работают с домашнего IP; my egress их тоже отдаёт) ---
# Хабр Карьера — RSS career.habr.com/vacancies/rss?q=... (IT РФ, junior/стажировки)
HABR_ENABLED = True
# getmatch.ru — JSON getmatch.ru/api/offers (IT РФ, часто с зарплатами)
GETMATCH_ENABLED = True

# --- Частота проверки ---
POLL_INTERVAL_MINUTES = 15

# --- Стоп-слова: пропускать вакансии, где в названии есть эти слова ---
TITLE_BLOCKLIST = [
    "senior", "lead", "тимлид", "руководитель", "middle+",
    "director", "head of", "principal", "vp ", "chief", "manager", "sales",
    "старший", "ведущий", "главный",
]

# User-Agent для hh.ru (обязателен; можно оставить как есть)
USER_AGENT = "JobHunterBot/1.0 (personal use)"

# --- P1: AI-фильтр вакансий (бесплатный LLM через Groq) ---
AI_FILTER_ENABLED = True
FIT_THRESHOLD = 55        # присылать только вакансии с fit_score >= порога
# Профиль кандидата — по нему LLM оценивает совпадение. Правь под себя:
MY_PROFILE = """
Junior-разработчик (Python), 1-й курс IT-колледжа. Стек: Python, FastAPI, aiogram,
SQL/SQLite, REST API, автоматизация/скрипты, Docker, Git; немного React/TypeScript.
Опыт: фриланс (Telegram-боты, веб-сервисы, лендинги), пет-проекты — бот-агрегатор
вакансий с интеграцией API, интернет-магазин Telegram Mini App с CI/CD.
Уровень: начинающий, без коммерческого стажа в найме. Английский: intermediate (B1).
Ищу: junior/стажировку по разработке (Python/бэкенд) или аналитике данных; удалённо или РФ.
Интересы: Python-бэкенд, работа с данными и API, крипта, AI/LLM.
""".strip()

