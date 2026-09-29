"""P1 — AI-фильтр вакансий на бесплатном LLM (Groq).

Оценивает, насколько вакансия подходит кандидату: даёт fit_score, вердикт,
совпадающие/недостающие навыки, проверку на entry-level и красные флаги (скам).
"""

import json
import re

import config
import llm

SYSTEM = (
    "Ты — опытный IT-рекрутер и карьерный консультант. По профилю кандидата и вакансии "
    "даёшь честную, конкретную и полезную оценку: подходит ли, что совпадает, чего не хватает, "
    "на что делать упор в отклике, нет ли скама. Не приукрашиваешь. "
    "Отвечай СТРОГО одним JSON-объектом на русском, без markdown и текста вокруг."
)


def _prompt(v: dict) -> str:
    desc = v.get("desc", "")
    desc_block = f"Описание: {desc}\n" if desc else ""
    return (
        f"КАНДИДАТ:\n{config.MY_PROFILE}\n\n"
        f"ВАКАНСИЯ:\n"
        f"Название: {v['name']}\n"
        f"Компания: {v['employer']}\n"
        f"Зарплата: {v['salary']}\n"
        f"Формат: {'удалённо' if v['remote'] else 'офис/гибрид'} · {v['area']}\n"
        f"{desc_block}\n"
        "Оцени и верни JSON СТРОГО такого вида (все поля обязательны):\n"
        "{\n"
        '  "fit_score": <целое 0-100 — насколько подходит кандидату>,\n'
        '  "verdict": "apply|maybe|skip",\n'
        '  "seniority": "стажёр|junior|middle|senior|не ясно",\n'
        '  "summary": "1-2 предложения: суть роли и чем занимается",\n'
        '  "key_requirements": ["главные требования вакансии, 2-4 пункта"],\n'
        '  "matched_skills": ["навыки кандидата, которые подходят"],\n'
        '  "missing_skills": ["чего кандидату не хватает под эту вакансию"],\n'
        '  "salary_comment": "короткий комментарий по зарплате или \\"не указана\\"",\n'
        '  "how_to_apply": "конкретный совет: на что сделать упор в отклике под ЭТУ вакансию",\n'
        '  "growth": "что эта работа даст для роста кандидата (1 фраза)",\n'
        '  "red_flags": ["признаки скама/проблем, если есть, иначе пустой список"],\n'
        '  "reason": "1-2 фразы: почему такой fit_score"\n'
        "}"
    )


def score(v: dict):
    """Вернуть dict с оценкой или None, если не удалось."""
    if not llm.available():
        return None
    try:
        content, _ = llm.chat(
            [{"role": "system", "content": SYSTEM},
             {"role": "user", "content": _prompt(v)}],
            max_tokens=1100, temperature=0.0,
        )
        m = re.search(r"\{.*\}", content, re.S)
        if not m:
            return None
        data = json.loads(m.group(0))
        # нормализация
        data["fit_score"] = int(data.get("fit_score", 0))
        data["verdict"] = str(data.get("verdict", "maybe")).lower()
        for k in ("matched_skills", "missing_skills", "red_flags", "key_requirements"):
            if not isinstance(data.get(k), list):
                data[k] = []
        for k in ("seniority", "summary", "salary_comment", "how_to_apply", "growth", "reason"):
            if not isinstance(data.get(k), str):
                data[k] = ""
        return data
    except Exception as e:
        print(f"[ai_filter] ошибка оценки: {e}")
        return None
