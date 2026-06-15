import threading
import time
from parser_utils import load_urls, divide_into_chunks, parse_gutenberg_book
from db import save_book_as_task, clear_tasks


def worker(urls_chunk):
    for url in urls_chunk:
        data = parse_gutenberg_book(url)
        if data:
            save_book_as_task(data)
            print(f"[THREAD] {data['title']} | {data['author']}")


def run_threading(num_threads=8):
    print("\n=== THREADING ===")
    urls = load_urls()
    clear_tasks()

    chunks = divide_into_chunks(urls, num_threads)
    threads = []
    start = time.perf_counter()

    for chunk in chunks:
        t = threading.Thread(target=worker, args=(chunk,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    elapsed = time.perf_counter() - start
    print(f"Threading: {elapsed:.4f} сек")
    return elapsed


if __name__ == "__main__":
    run_threading()