"""Источник — Jobicy (международная удалёнка). Публичный JSON API, ключ не нужен.
Отдаёт свежие remote-вакансии; фильтруем по ключам под профиль."""

import requests
import config

API = "https://jobicy.com/api/v2/remote-jobs"


def _blocked(title: str) -> bool:
    t = title.lower()
    return any(w in t for w in config.TITLE_BLOCKLIST)


def _salary(j):
    lo, hi, cur = j.get("salaryMin"), j.get("salaryMax"), j.get("salaryCurrency") or ""
    try:
        lo, hi = int(lo), int(hi)
    except (TypeError, ValueError):
        return "з/п не указана"
    if lo and hi:
        return f"{cur} {lo:,}–{hi:,}"
    if lo:
        return f"от {cur} {lo:,}"
    return "з/п не указана"


def fetch():
    if not getattr(config, "JOBICY_ENABLED", True):
        return []
    try:
        r = requests.get(API, params={"count": 50}, headers={"User-Agent": config.USER_AGENT}, timeout=25)
        r.raise_for_status()
        jobs = r.json().get("jobs", [])
    except Exception as e:
        print(f"[jobicy] ошибка запроса: {e}")
        return []

    result = []
    for j in jobs:
        title = j.get("jobTitle", "")
        if not title or _blocked(title):
            continue
        hay = (title + " " + " ".join(j.get("jobIndustry") or [])).lower()
        kw = next((k for k in config.REMOTEOK_KEYWORDS if k.lower() in hay), None)
        if not kw:
            continue
        result.append({
            "id": f"jbcy:{j.get('id')}",
            "name": title,
            "employer": j.get("companyName", "—"),
            "salary": _salary(j),
            "area": j.get("jobGeo") or "🌍 Remote",
            "url": j.get("url", ""),
            "remote": True,
            "desc": config.strip_html(j.get("jobExcerpt", "")),
            "matched": f"Jobicy · {kw}",
        })
    return result
