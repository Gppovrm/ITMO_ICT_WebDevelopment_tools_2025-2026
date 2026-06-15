import multiprocessing
import time
from parser_utils import load_urls, divide_into_chunks, parse_gutenberg_book
from db import save_book_as_task, clear_tasks


def worker(urls_chunk):
    for url in urls_chunk:
        data = parse_gutenberg_book(url)
        if data:
            save_book_as_task(data)
            print(f"[PROCESS] {data['title']} | {data['author']}")


def run_multiprocessing(num_processes=8):
    print("\n=== MULTIPROCESSING ===")
    urls = load_urls()
    clear_tasks()

    chunks = divide_into_chunks(urls, num_processes)
    processes = []
    start = time.perf_counter()

    for chunk in chunks:
        p = multiprocessing.Process(target=worker, args=(chunk,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    elapsed = time.perf_counter() - start
    print(f"Multiprocessing: {elapsed:.4f} сек")
    return elapsed


if __name__ == "__main__":
    multiprocessing.freeze_support()
    run_multiprocessing()
