import time
from sum_range import sum_range

TOTAL = 100_000_000


def main():
    start_time = time.perf_counter()
    result = sum_range(1, TOTAL)
    elapsed = time.perf_counter() - start_time

    print(f"Синхронный подсчёт (цикл)")
    print(f"Сумма от 1 до {TOTAL}: {result}")
    print(f"Время: {elapsed:.4f} сек")


if __name__ == "__main__":
    main()