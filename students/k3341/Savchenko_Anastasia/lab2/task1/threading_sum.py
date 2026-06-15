import threading
import time
from sum_range import sum_range

TOTAL = 100_000_000
NUM_THREADS = 8


def worker(start, end, results, index):
    partial = sum_range(start, end)
    results[index] = partial
    print(f"Поток {index}: [{start}, {end}] готов")


def main():
    chunk_size = TOTAL // NUM_THREADS
    results = [0] * NUM_THREADS
    threads = []

    start_time = time.perf_counter()

    for i in range(NUM_THREADS):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < NUM_THREADS - 1 else TOTAL
        t = threading.Thread(target=worker, args=(start, end, results, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total = sum(results)
    elapsed = time.perf_counter() - start_time

    print(f"\nThreading результат")
    print(f"Сумма: {total}")
    print(f"Время: {elapsed:.4f} сек")


if __name__ == "__main__":
    main()