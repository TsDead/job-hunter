"""P1 — AI-фильтр вакансий на бесплатном LLM (Groq).

Оценивает, насколько вакансия подходит кандидату: даёт fit_score, вердикт,
совпадающие/недостающие навыки, проверку на entry-level и красные флаги (скам).
"""

import json
import re

import config
import llm

SYSTEM = (
    "Ты — ассистент по подбору работы. По профилю кандидата и описанию вакансии "
    "оцениваешь, насколько они совпадают. Отвечай СТРОГО одним JSON-объектом на русском, "
    "без markdown и пояснений вокруг."
)


def _prompt(v: dict) -> str:
    return (
        f"КАНДИДАТ:\n{config.MY_PROFILE}\n\n"
        f"ВАКАНСИЯ:\n"
        f"Название: {v['name']}\n"
        f"Компания: {v['employer']}\n"
        f"Зарплата: {v['salary']}\n"
        f"Формат: {'удалённо' if v['remote'] else 'офис/гибрид'} · {v['area']}\n"
        f"Найдена по запросу: {v['matched']}\n\n"
        "Верни JSON строго такого вида:\n"
        '{"fit_score": <целое 0-100>, "verdict": "apply|maybe|skip", '
        '"matched_skills": ["..."], "missing_skills": ["..."], '
        '"is_entry_level": true|false, "red_flags": ["..."], '
        '"reason": "одна короткая фраза почему"}'
    )


def score(v: dict):
    """Вернуть dict с оценкой или None, если не удалось."""
    if not llm.available():
        return None
    try:
        content, _ = llm.chat(
            [{"role": "system", "content": SYSTEM},
             {"role": "user", "content": _prompt(v)}],
            max_tokens=700, temperature=0.0,
        )
        m = re.search(r"\{.*\}", content, re.S)
        if not m:
            return None
        data = json.loads(m.group(0))
        # нормализация
        data["fit_score"] = int(data.get("fit_score", 0))
        data["verdict"] = str(data.get("verdict", "maybe")).lower()
        for k in ("matched_skills", "missing_skills", "red_flags"):
            if not isinstance(data.get(k), list):
                data[k] = []
        return data
    except Exception as e:
        print(f"[ai_filter] ошибка оценки: {e}")
        return None
