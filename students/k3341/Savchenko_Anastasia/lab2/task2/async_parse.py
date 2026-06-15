import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup
from parser_utils import load_urls
from db import save_book_as_task, clear_tasks
from config import HEADERS


async def parse_page_async(session, url):
    try:
        await asyncio.sleep(0.3)
        async with session.get(url, timeout=15) as response:
            if response.status != 200:
                print(f"[ASYNC] {url} -> статус {response.status}, пропускаем")
                return None

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            title = "Unknown title"
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
                if " by " in title:
                    title = title.split(" by ")[0]

            author = "Unknown author"
            bibrec = soup.find('table', class_='bibrec')
            if bibrec:
                for row in bibrec.find_all('tr'):
                    th = row.find('th')
                    if th and 'Author' in th.get_text():
                        td = row.find('td')
                        if td:
                            author = td.get_text(strip=True)
                            author = author.split(';')[0].split(',')[0].strip()
                            break

            gutenberg_id = int(url.split('/')[-1])

            return {
                "url": url,
                "title": title[:200],
                "author": author[:100],
                "gutenberg_id": gutenberg_id,
                "priority": 3
            }
    except Exception as e:
        print(f"[ASYNC ERROR] {url}: {e}")
        return None


async def run_async_logic():
    urls = load_urls()
    clear_tasks()

    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(headers=HEADERS, connector=connector) as session:
        tasks = [parse_page_async(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

        for data in results:
            if data:
                save_book_as_task(data)
                print(f"[ASYNC] {data['title']} | {data['author']}")


def run_async():
    print("\n=== ASYNCIO ===")
    start = time.perf_counter()
    asyncio.run(run_async_logic())
    elapsed = time.perf_counter() - start
    print(f"Async: {elapsed:.4f} сек")
    return elapsed


if __name__ == "__main__":
    run_async()
