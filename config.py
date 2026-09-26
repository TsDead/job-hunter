"""Настройки бота-охотника за вакансиями.
Правь этот файл под себя — поисковые запросы, регион, частоту проверки."""

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

# --- Фильтры hh.ru ---
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
    "python", "django", "fastapi", "backend",
    "ai", "machine learning", "ml", "llm",
    "data", "junior", "intern", "qa",
]

# --- Частота проверки ---
POLL_INTERVAL_MINUTES = 15

# --- Стоп-слова: пропускать вакансии, где в названии есть эти слова ---
TITLE_BLOCKLIST = ["senior", "lead", "тимлид", "руководитель", "middle+"]

# User-Agent для hh.ru (обязателен; можно оставить как есть)
USER_AGENT = "JobHunterBot/1.0 (personal use)"
