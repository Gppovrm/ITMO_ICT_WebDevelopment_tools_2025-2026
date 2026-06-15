import multiprocessing
from threading_parse import run_threading
from multiprocessing_parse import run_multiprocessing
from async_parse import run_async


def main():
    print("=" * 60)
    print("ЛАБОРАТОРНАЯ РАБОТА №2")
    print("ЗАДАЧА 2: ПАРАЛЛЕЛЬНЫЙ ПАРСИНГ ВЕБ-СТРАНИЦ")
    print("Источник: Project Gutenberg (книги как задачи в тайм-менеджере)")
    print("=" * 60)

    results = {}

    print("\n[1/3] Запуск Threading...")
    results["Threading"] = run_threading(num_threads=8)

    print("\n[2/3] Запуск Multiprocessing...")
    results["Multiprocessing"] = run_multiprocessing(num_processes=8)

    print("\n[3/3] Запуск Asyncio...")
    results["Asyncio"] = run_async()

    print("\n" + "=" * 60)
    print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print("=" * 60)
    print(f"{'Подход':<20} | {'Время (сек)':<15}")
    print("-" * 40)

    for approach, elapsed in results.items():
        print(f"{approach:<20} | {elapsed:.4f} сек")

    print("=" * 60)
    fastest = min(results, key=results.get)
    print(f"\n🏆 Самый быстрый: {fastest} ({results[fastest]:.4f} сек)")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
