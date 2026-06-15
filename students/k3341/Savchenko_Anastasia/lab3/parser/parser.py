import math
import requests
import time
from bs4 import BeautifulSoup
from pathlib import Path
from config import HEADERS


def load_urls(filename="urls.txt"):
    path = Path(__file__).parent / filename
    urls = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith('\ufeff'):
                line = line[1:]
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def divide_into_chunks(lst, num_chunks):
    if not lst:
        return []
    chunk_size = math.ceil(len(lst) / num_chunks)
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def parse_gutenberg_book(url):
    try:
        time.sleep(0.3)
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

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
        print(f"[ERROR] {url}: {e}")
        return None
