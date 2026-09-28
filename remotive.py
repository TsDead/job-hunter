"""Третий источник — Remotive (международная удалёнка). Публичный JSON API, ключ не нужен.
Работает из любых сетей (как RemoteOK, в отличие от hh.ru). Вакансии на английском."""

import requests
import config

API = "https://remotive.com/api/remote-jobs"

# Поисковые термины под профиль (Remotive ищет по названию/описанию)
SEARCHES = ["python", "machine learning", "ai engineer", "backend", "data analyst", "junior developer"]


def _blocked(title: str) -> bool:
    t = title.lower()
    return any(w in t for w in config.TITLE_BLOCKLIST)


def fetch():
    if not getattr(config, "REMOTIVE_ENABLED", True):
        return []
    headers = {"User-Agent": config.USER_AGENT}
    seen, result = set(), []
    for term in SEARCHES:
        try:
            r = requests.get(API, params={"search": term, "limit": 30}, headers=headers, timeout=25)
            r.raise_for_status()
            jobs = r.json().get("jobs", [])
        except Exception as e:
            print(f"[remotive] ошибка запроса '{term}': {e}")
            continue
        for j in jobs:
            jid = j.get("id")
            title = j.get("title", "")
            if not jid or jid in seen or not title or _blocked(title):
                continue
            seen.add(jid)
            result.append({
                "id": f"rmtv:{jid}",
                "name": title,
                "employer": j.get("company_name", "—"),
                "salary": (j.get("salary") or "").strip() or "з/п не указана",
                "area": j.get("candidate_required_location") or "🌍 Remote",
                "url": j.get("url", ""),
                "remote": True,
                "matched": f"Remotive · {term}",
            })
    return result
