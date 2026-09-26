"""Бот-охотник за вакансиями: поллит hh.ru и шлёт новые вакансии в Telegram.

Запуск:
    python main.py           # бесконечный цикл (проверка каждые N минут)
    python main.py --once    # один прогон и выход (для теста / cron / GitHub Actions)
"""

import sys
import time

import config
import hh
import remoteok
import storage
import notifier


def collect() -> list:
    """Собрать вакансии из всех источников (hh.ru + RemoteOK), убрать дубли по id."""
    vacancies = hh.fetch() + remoteok.fetch()
    uniq = {}
    for v in vacancies:
        uniq[v["id"]] = v
    return list(uniq.values())


def run_once(first_run: bool) -> int:
    """Один цикл проверки. Возвращает число отправленных уведомлений."""
    vacancies = collect()
    new = [v for v in vacancies if storage.is_new(v["id"])]

    if first_run:
        # Первый запуск: не спамим всей выдачей — помечаем как виденные молча.
        for v in new:
            storage.mark(v["id"])
        notifier.send_text(
            f"🤖 <b>Job-hunter запущен.</b>\n"
            f"Слежу за {len(config.SEARCHES)} запросами по России "
            f"({'с удалёнкой' if config.INCLUDE_REMOTE else 'без удалёнки'}).\n"
            f"В базе отмечено {len(new)} текущих вакансий — с этого момента "
            f"буду присылать только <b>новые</b>."
        )
        return 0

    sent = 0
    # шлём от старых к новым, чтобы в чате свежие были снизу
    for v in reversed(new):
        notifier.send_vacancy(v)
        storage.mark(v["id"])
        sent += 1
        time.sleep(0.4)  # мягкая пауза для Telegram
    return sent


def main():
    once = "--once" in sys.argv
    first_run = storage.count() == 0

    if first_run:
        print("Первый запуск — заполняю базу текущими вакансиями (без спама).")

    while True:
        try:
            sent = run_once(first_run)
            print(f"[{time.strftime('%H:%M:%S')}] проверка завершена, новых отправлено: {sent}")
        except Exception as e:
            print(f"[main] ошибка цикла: {e}")
        first_run = False

        if once:
            break
        time.sleep(config.POLL_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main()
