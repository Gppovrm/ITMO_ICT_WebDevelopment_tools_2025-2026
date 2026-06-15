import multiprocessing
import time
from sum_range import sum_range

TOTAL = 100_000_000
NUM_PROCESSES = 8


def worker(start, end):
    return sum_range(start, end)


def main():
    chunk_size = TOTAL // NUM_PROCESSES
    tasks = []

    for i in range(NUM_PROCESSES):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < NUM_PROCESSES - 1 else TOTAL
        tasks.append((start, end))

    start_time = time.perf_counter()

    with multiprocessing.Pool(processes=NUM_PROCESSES) as pool:
        results = pool.starmap(worker, tasks)

    total = sum(results)
    elapsed = time.perf_counter() - start_time

    print(f"\nMultiprocessing результат")
    print(f"Сумма: {total}")
    print(f"Время: {elapsed:.4f} сек")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()