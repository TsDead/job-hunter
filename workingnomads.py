"""Источник — Working Nomads (международная удалёнка). Публичный JSON API, ключ не нужен.
Отдаёт список remote-вакансий; фильтруем по ключам под профиль."""

import requests
import config

API = "https://www.workingnomads.com/api/exposed_jobs/"


def _blocked(title: str) -> bool:
    t = title.lower()
    return any(w in t for w in config.TITLE_BLOCKLIST)


def fetch():
    if not getattr(config, "WORKINGNOMADS_ENABLED", True):
        return []
    try:
        r = requests.get(API, headers={"User-Agent": config.USER_AGENT}, timeout=25)
        r.raise_for_status()
        jobs = r.json()
    except Exception as e:
        print(f"[workingnomads] ошибка запроса: {e}")
        return []

    result = []
    for j in jobs:
        title = j.get("title", "")
        if not title or _blocked(title):
            continue
        hay = (title + " " + str(j.get("tags") or "") + " " + str(j.get("category_name") or "")).lower()
        kw = next((k for k in config.REMOTEOK_KEYWORDS if k.lower() in hay), None)
        if not kw:
            continue
        url = j.get("url", "")
        result.append({
            "id": f"wn:{url}",
            "name": title,
            "employer": j.get("company_name", "—"),
            "salary": "з/п не указана",
            "area": j.get("location") or "🌍 Remote",
            "url": url,
            "remote": True,
            "matched": f"WorkingNomads · {kw}",
        })
    return result
