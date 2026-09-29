"""Источник — getmatch.ru, РФ IT-рынок (часто с зарплатами). Публичный JSON API, ключ не нужен."""

import requests
import config

API = "https://getmatch.ru/api/offers"
BASE = "https://getmatch.ru"


def _blocked(title: str) -> bool:
    t = title.lower()
    return any(w in t for w in config.TITLE_BLOCKLIST)


def _salary(o):
    if o.get("salary_description"):
        return config.strip_html(o["salary_description"], 60)
    lo, hi, cur = o.get("salary_display_from"), o.get("salary_display_to"), o.get("salary_currency") or "₽"
    if lo and hi:
        return f"{lo:,}–{hi:,} {cur}".replace(",", " ")
    if lo:
        return f"от {lo:,} {cur}".replace(",", " ")
    return "з/п не указана"


def fetch():
    if not getattr(config, "GETMATCH_ENABLED", True):
        return []
    headers = {"User-Agent": config.USER_AGENT, "Accept": "application/json", "Accept-Language": "ru"}
    try:
        r = requests.get(API, headers=headers, timeout=25)
        r.raise_for_status()
        offers = r.json().get("offers", [])
    except Exception as e:
        print(f"[getmatch] ошибка запроса: {e}")
        return []

    result = []
    for o in offers:
        if not o.get("is_active"):
            continue
        title = o.get("position", "")
        if not title or _blocked(title):
            continue
        skills = " ".join(s.get("title", "") if isinstance(s, dict) else str(s) for s in (o.get("skills_objects") or []))
        hay = (title + " " + skills).lower()
        kw = next((k for k in config.REMOTEOK_KEYWORDS if k.lower() in hay), None)
        if not kw:
            continue
        locs = o.get("location_items") or []
        fmts = {l.get("format", "") for l in locs}
        remote = "remote" in fmts and not ({"office", "hybrid"} & fmts)
        area = ", ".join(l.get("label", "") for l in locs if l.get("label")) or "🌍 Удалённо"
        url = o.get("url", "")
        result.append({
            "id": f"gm:{o.get('id')}",
            "name": title,
            "employer": (o.get("company") or {}).get("name", "—"),
            "salary": _salary(o),
            "area": area,
            "url": BASE + url if url.startswith("/") else url,
            "remote": remote,
            "desc": config.strip_html(o.get("offer_description", "")),
            "matched": f"getmatch · {kw}",
        })
    return result
