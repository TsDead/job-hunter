"""Источник — Хабр Карьера (career.habr.com), РФ-рынок IT. Публичный RSS, ключ не нужен.
Отдаёт вакансии по текстовому запросу; парсим стандартной xml.etree."""

import re
import xml.etree.ElementTree as ET

import requests
import config

RSS = "https://career.habr.com/vacancies/rss"

# Поисковые термины под профиль (РФ-рынок, junior/стажировки)
SEARCHES = ["python", "junior", "стажёр", "backend", "machine learning", "аналитик данных", "QA python"]

# «Требуется «Python-разработчик» (Москва)» → вытащить название и город
_TITLE = re.compile(r"«(.+?)»\s*(?:\(([^)]+)\))?")


def _blocked(title: str) -> bool:
    t = title.lower()
    return any(w in t for w in config.TITLE_BLOCKLIST)


def fetch():
    if not getattr(config, "HABR_ENABLED", True):
        return []
    headers = {"User-Agent": config.USER_AGENT, "Accept-Language": "ru"}
    seen, result = set(), []
    for term in SEARCHES:
        try:
            r = requests.get(RSS, params={"q": term, "type": "all"}, headers=headers, timeout=25)
            r.raise_for_status()
            items = ET.fromstring(r.text).findall(".//item")
        except Exception as e:
            print(f"[habr] ошибка запроса '{term}': {e}")
            continue
        for it in items:
            raw = (it.findtext("title") or "").strip()
            link = (it.findtext("link") or "").strip()
            if not link or link in seen:
                continue
            m = _TITLE.search(raw)
            name = (m.group(1) if m else raw).strip()
            city = (m.group(2) if m and m.group(2) else "").strip()
            if not name or _blocked(name):
                continue
            kw = next((k for k in config.REMOTEOK_KEYWORDS if k.lower() in name.lower()), None)
            if not kw:
                continue
            seen.add(link)
            desc = config.strip_html(it.findtext("description") or "")
            remote = any(w in (name + " " + desc).lower() for w in ("удал", "remote", "из дома"))
            result.append({
                "id": f"habr:{link.rsplit('/', 1)[-1]}",
                "name": name,
                "employer": (it.findtext("author") or "—").strip() or "—",
                "salary": "з/п не указана",
                "area": city or ("🌍 Удалённо" if remote else "Россия"),
                "url": link,
                "remote": remote,
                "desc": desc,
                "matched": f"Хабр Карьера · {kw}",
            })
    return result
