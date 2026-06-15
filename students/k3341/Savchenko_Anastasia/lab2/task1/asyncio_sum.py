import asyncio
import time
from sum_range import sum_range

TOTAL = 100_000_000
NUM_TASKS = 8


async def worker(start, end):
    return sum_range(start, end)


async def main():
    chunk_size = TOTAL // NUM_TASKS
    tasks = []

    for i in range(NUM_TASKS):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < NUM_TASKS - 1 else TOTAL
        tasks.append(asyncio.create_task(worker(start, end)))

    results = await asyncio.gather(*tasks)
    return sum(results)


if __name__ == "__main__":
    start_time = time.perf_counter()
    total = asyncio.run(main())
    elapsed = time.perf_counter() - start_time

    print(f"\nAsyncio результат")
    print(f"Сумма: {total}")
    print(f"Время: {elapsed:.4f} сек")