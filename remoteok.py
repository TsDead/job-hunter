"""Второй источник — RemoteOK (международная удалёнка). Публичный JSON, ключ не нужен.
Работает и из дата-центров (в отличие от hh.ru). Вакансии на английском."""

import requests
import config

API = "https://remoteok.com/api"


def _fmt_salary(job):
    lo, hi = job.get("salary_min") or 0, job.get("salary_max") or 0
    if lo and hi:
        return f"${lo:,}–${hi:,}/год"
    if lo:
        return f"от ${lo:,}/год"
    return "з/п не указана"


def _match(job) -> str | None:
    """Вернуть ключевое слово, по которому вакансия подходит, иначе None."""
    hay = (job.get("position", "") + " " + " ".join(job.get("tags", []))).lower()
    if any(b in hay for b in config.TITLE_BLOCKLIST):
        return None
    for kw in config.REMOTEOK_KEYWORDS:
        if kw.lower() in hay:
            return kw
    return None


def fetch():
    if not getattr(config, "REMOTEOK_ENABLED", False):
        return []
    headers = {"User-Agent": config.USER_AGENT + " Mozilla/5.0"}
    try:
        r = requests.get(API, headers=headers, timeout=25)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[remoteok] ошибка запроса: {e}")
        return []

    result = []
    for job in data:
        if not job.get("position"):   # первый элемент — метаданные/legal
            continue
        kw = _match(job)
        if not kw:
            continue
        result.append({
            "id": f"rok:{job.get('id')}",
            "name": job.get("position", "—"),
            "employer": job.get("company", "—"),
            "salary": _fmt_salary(job),
            "area": job.get("location") or "🌍 Remote",
            "url": job.get("url", ""),
            "remote": True,
            "desc": config.strip_html(job.get("description", "")),
            "matched": f"RemoteOK · {kw}",
        })
    return result
