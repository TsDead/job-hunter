"""Урок 2 — тестирование API через requests + pytest.

Именно это делают QA Automation инженеры: дёргают API и проверяют ответ.
Тестируем публичное учебное API https://jsonplaceholder.typicode.com
(бесплатное, специально сделано для тренировки — ничего не сломаешь).

Запуск:  python -m pytest tests/test_api.py -v
"""

import requests
import pytest

BASE = "https://jsonplaceholder.typicode.com"


# ---------- 1. Проверяем статус-код ----------
# Первое, что проверяет любой API-тест: сервер ответил 200 (ОК)?

def test_get_возвращает_200():
    r = requests.get(f"{BASE}/posts/1", timeout=15)
    assert r.status_code == 200        # 200 = успех


# ---------- 2. Проверяем содержимое ответа (JSON) ----------
# Мало что 200 — надо убедиться, что в теле правильные данные.

def test_пост_имеет_нужные_поля():
    r = requests.get(f"{BASE}/posts/1", timeout=15)
    data = r.json()                    # превращаем JSON-ответ в словарь Python
    assert data["id"] == 1             # id именно тот, что запросили
    assert "title" in data             # поле title вообще есть
    assert "body" in data
    assert isinstance(data["title"], str)   # и это строка, а не что-то странное


# ---------- 3. Параметризация: проверяем сразу несколько записей ----------

@pytest.mark.parametrize("post_id", [1, 5, 10, 50, 100])
def test_разные_посты_доступны(post_id):
    r = requests.get(f"{BASE}/posts/{post_id}", timeout=15)
    assert r.status_code == 200
    assert r.json()["id"] == post_id


# ---------- 4. Негативный тест: чего НЕ должно быть ----------
# Хороший тестировщик проверяет и ошибки: несуществующий пост → 404.

def test_несуществующий_пост_даёт_404():
    r = requests.get(f"{BASE}/posts/99999", timeout=15)
    assert r.status_code == 404


# ---------- 5. Проверяем список и его длину ----------

def test_список_постов_не_пустой():
    r = requests.get(f"{BASE}/posts", timeout=15)
    posts = r.json()
    assert isinstance(posts, list)     # это список
    assert len(posts) == 100           # у этого API ровно 100 постов


# ---------- 6. POST-запрос: создаём ресурс и проверяем ответ ----------
# Не только читать (GET), но и отправлять данные (POST) — тоже часть API-тестов.

def test_создание_поста():
    новый = {"title": "мой тест", "body": "текст", "userId": 1}
    r = requests.post(f"{BASE}/posts", json=новый, timeout=15)
    assert r.status_code == 201         # 201 = "создано"
    ответ = r.json()
    assert ответ["title"] == "мой тест" # сервер вернул то, что мы отправили
    assert "id" in ответ                # и присвоил новому посту id
