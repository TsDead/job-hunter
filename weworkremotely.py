"""Источник — We Work Remotely (одна из крупнейших remote-tech площадок).
Публичные RSS-ленты по категориям, ключ не нужен. Парсим стандартной xml.etree.
Формат заголовка в RSS: "Компания: Должность"."""

import xml.etree.ElementTree as ET

import requests
import config

# Категории RSS под профиль (программирование / бэкенд / девопс)
FEEDS = [
    "remote-programming-jobs",
    "remote-back-end-programming-jobs",
    "remote-devops-sysadmin-jobs",
]
BASE = "https://weworkremotely.com/categories/{}.rss"


def _blocked(title: str) -> bool:
    t = title.lower()
    return any(w in t for w in config.TITLE_BLOCKLIST)


def fetch():
    if not getattr(config, "WWR_ENABLED", True):
        return []
    headers = {"User-Agent": config.USER_AGENT}
    seen, result = set(), []
    for cat in FEEDS:
        try:
            r = requests.get(BASE.format(cat), headers=headers, timeout=25)
            r.raise_for_status()
            items = ET.fromstring(r.text).findall(".//item")
        except Exception as e:
            print(f"[wwr] ошибка ленты '{cat}': {e}")
            continue
        for it in items:
            title = (it.findtext("title") or "").strip()
            link = (it.findtext("link") or "").strip()
            if not title or not link or link in seen:
                continue
            if ": " in title:
                company, position = title.split(": ", 1)
            else:
                company, position = "—", title
            if _blocked(position):
                continue
            kw = next((k for k in config.REMOTEOK_KEYWORDS if k.lower() in position.lower()), None)
            if not kw:
                continue
            seen.add(link)
            result.append({
                "id": f"wwr:{link}",
                "name": position.strip(),
                "employer": company.strip(),
                "salary": "з/п не указана",
                "area": "🌍 Remote",
                "url": link,
                "remote": True,
                "matched": f"WeWorkRemotely · {kw}",
            })
    return result
