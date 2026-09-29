"""Автотесты для функций бота job-hunter — учебный пример pytest.

Как запускать (из папки job-hunter):
    python -m pytest -v

Что важно знать про pytest:
1. Файлы с тестами называются test_*.py, функции — test_*().
2. Внутри теста ты просто пишешь `assert <условие>` — если оно False, тест падает.
3. pytest сам находит все test_-функции и запускает их.
"""

import config
import remoteok
import jobicy
import himalayas


# ---------- 1. Самый простой тест: одна проверка ----------

def test_strip_html_убирает_теги():
    # берём строку с HTML-тегами и проверяем, что они исчезли
    результат = config.strip_html("<b>Привет</b> <i>мир</i>")
    assert результат == "Привет мир"


def test_strip_html_на_пустой_строке():
    # граничный случай: пустой ввод не должен ломать функцию
    assert config.strip_html("") == ""
    assert config.strip_html(None) == ""


def test_strip_html_обрезает_по_лимиту():
    # длинную строку функция должна обрезать до limit символов
    длинная = "a" * 1000
    assert len(config.strip_html(длинная, limit=100)) == 100


# ---------- 2. Параметризация: один тест — много случаев ----------
# @pytest.mark.parametrize прогоняет тест на КАЖДОМ наборе данных.
# Это заменяет десять почти одинаковых тестов одним.

import pytest


@pytest.mark.parametrize("min_zp, max_zp, ожидаем", [
    (50000, 70000, "$50,000–$70,000/год"),   # обе границы есть
    (60000, 0,     "от $60,000/год"),          # только нижняя
    (0,     0,     "з/п не указана"),          # ничего не указано
])
def test_remoteok_формат_зарплаты(min_zp, max_zp, ожидаем):
    job = {"salary_min": min_zp, "salary_max": max_zp}
    assert remoteok._fmt_salary(job) == ожидаем


# ---------- 3. Тестируем зарплату Jobicy ----------

def test_jobicy_зарплата_с_вилкой():
    оффер = {"salaryMin": 100000, "salaryMax": 120000, "salaryCurrency": "USD"}
    assert jobicy._salary(оффер) == "USD 100,000–120,000"


def test_jobicy_зарплата_не_указана():
    # если чисел нет — должна вернуться заглушка, а не ошибка
    assert jobicy._salary({"salaryMin": None, "salaryMax": None}) == "з/п не указана"


# ---------- 4. Fixture: общие данные для нескольких тестов ----------
# Функция с @pytest.fixture готовит данные, а тесты получают их как аргумент.
# Удобно, когда один и тот же объект нужен в разных тестах.

@pytest.fixture
def вакансия_himalayas():
    return {"minSalary": 3000, "maxSalary": 5000, "currency": "USD"}


def test_himalayas_зарплата(вакансия_himalayas):
    assert himalayas._salary(вакансия_himalayas) == "USD 3,000–5,000"


def test_himalayas_без_зарплаты():
    assert himalayas._salary({"minSalary": None, "maxSalary": None}) == "з/п не указана"
