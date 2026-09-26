"""Источник вакансий — API HeadHunter (hh.ru). Ключ не нужен, только User-Agent."""

import requests
import config

API = "https://api.hh.ru/vacancies"


def _params(text: str, remote: bool):
    p = {
        "text": text,
        "area": config.AREA,
        "experience": config.EXPERIENCE,
        "period": config.PERIOD_DAYS,
        "per_page": config.PER_PAGE,
        "order_by": "publication_time",
    }
    if remote:
        p["schedule"] = "remote"
    return p


def _fmt_salary(s):
    if not s:
        return "з/п не указана"
    lo, hi, cur = s.get("from"), s.get("to"), s.get("currency", "")
    if lo and hi:
        return f"{lo}–{hi} {cur}"
    if lo:
        return f"от {lo} {cur}"
    if hi:
        return f"до {hi} {cur}"
    return "з/п не указана"


def _blocked(title: str) -> bool:
    t = title.lower()
    return any(w in t for w in config.TITLE_BLOCKLIST)


def fetch():
    """Вернуть список вакансий (уникальных по id) по всем запросам из config.SEARCHES."""
    headers = {"User-Agent": config.USER_AGENT}
    seen_ids = set()
    result = []

    modes = [False]
    if config.INCLUDE_REMOTE:
        modes.append(True)

    for text in config.SEARCHES:
        for remote in modes:
            try:
                r = requests.get(API, params=_params(text, remote), headers=headers, timeout=20)
                r.raise_for_status()
                items = r.json().get("items", [])
            except Exception as e:
                print(f"[hh] ошибка запроса '{text}' remote={remote}: {e}")
                continue

            for it in items:
                vid = it.get("id")
                if not vid or vid in seen_ids:
                    continue
                if _blocked(it.get("name", "")):
                    continue
                seen_ids.add(vid)
                result.append({
                    "id": f"hh:{vid}",
                    "name": it.get("name", "—"),
                    "employer": (it.get("employer") or {}).get("name", "—"),
                    "salary": _fmt_salary(it.get("salary")),
                    "area": (it.get("area") or {}).get("name", "—"),
                    "url": it.get("alternate_url", ""),
                    "remote": remote,
                    "matched": text,
                })
    return result
