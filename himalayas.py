"""Источник — Himalayas (международная удалёнка). Публичный JSON API, ключ не нужен.
Отдаёт remote-вакансии с зарплатой и уровнем; фильтруем по ключам под профиль."""

import requests
import config

API = "https://himalayas.app/jobs/api"


def _blocked(title: str) -> bool:
    t = title.lower()
    return any(w in t for w in config.TITLE_BLOCKLIST)


def _salary(j):
    lo, hi, cur = j.get("minSalary"), j.get("maxSalary"), j.get("currency") or ""
    try:
        lo, hi = int(lo), int(hi)
    except (TypeError, ValueError):
        return "з/п не указана"
    if lo and hi:
        return f"{cur} {lo:,}–{hi:,}"
    return "з/п не указана"


def fetch():
    if not getattr(config, "HIMALAYAS_ENABLED", True):
        return []
    try:
        r = requests.get(API, params={"limit": 50}, headers={"User-Agent": config.USER_AGENT}, timeout=25)
        r.raise_for_status()
        jobs = r.json().get("jobs", [])
    except Exception as e:
        print(f"[himalayas] ошибка запроса: {e}")
        return []

    result = []
    for j in jobs:
        title = j.get("title", "")
        if not title or _blocked(title):
            continue
        if str(j.get("seniority", "")).lower() in ("senior", "lead", "principal", "staff"):
            continue
        hay = (title + " " + " ".join(j.get("categories") or [])).lower()
        kw = next((k for k in config.REMOTEOK_KEYWORDS if k.lower() in hay), None)
        if not kw:
            continue
        loc = ", ".join(j.get("locationRestrictions") or []) or "🌍 Remote"
        result.append({
            "id": f"him:{j.get('guid')}",
            "name": title,
            "employer": j.get("companyName", "—"),
            "salary": _salary(j),
            "area": loc,
            "url": j.get("applicationLink", ""),
            "remote": True,
            "desc": config.strip_html(j.get("excerpt") or j.get("description", "")),
            "matched": f"Himalayas · {kw}",
        })
    return result
