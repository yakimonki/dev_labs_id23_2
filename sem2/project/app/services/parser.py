import uuid
import asyncio
import os
from urllib.parse import urljoin, urlparse
from typing import Set, Dict
import requests
from bs4 import BeautifulSoup
import networkx as nx
from app.core.config import settings

class WebsiteParser:
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.base_dir = settings.DATA_DIR

    async def is_valid_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    async def is_internal_link(self, url: str, base_domain: str) -> bool:
        return urlparse(url).netloc == base_domain

    async def normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed._replace(fragment="", query="").geturl()

    async def get_page_links(self, url: str, base_domain: str) -> Set[str]:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()

            if 'text/html' not in response.headers.get('content-type', ''):
                return set()

            soup = BeautifulSoup(response.text, 'html.parser')
            links = set()

            for link in soup.find_all('a', href=True):
                href = link.get('href')
                abs_url = urljoin(url, href)
                norm_url = await self.normalize_url(abs_url)

                if await self.is_valid_url(norm_url) and await self.is_internal_link(norm_url, base_domain):
                    links.add(norm_url)

            return links

        except requests.exceptions.RequestException as e:
            print(f"Error processing {url}: {e}")
            return set()

    async def crawl_website(self, url: str, max_depth: int, task_id: str):
        queue = [(url, 0)]
        visited: Set[str] = set()
        graph = nx.DiGraph()
        total_urls = 0
        visited.add(url)
        graph.add_node(url)
        base_domain = urlparse(url).netloc

        while queue:
            current_url, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            links = await self.get_page_links(current_url, base_domain)
            for link in links:
                if link not in visited:
                    visited.add(link)
                    queue.append((link, depth + 1))
                    total_urls += 1
                    progress = min((len(visited) / total_urls) * 100 if total_urls > 0 else 0, 100)
                    self.tasks[task_id] = {"status": "in_progress", "progress": int(progress), "result": None}
                graph.add_edge(current_url, link)

            await asyncio.sleep(0.1)  # Небольшая задержка для обновления статуса

        self.tasks[task_id] = {"status": "completed", "progress": 100, "result": None}
        os.makedirs(self.base_dir, exist_ok=True)
        filepath = os.path.join(self.base_dir, f"graph_{task_id}.graphml")
        nx.write_graphml(graph, filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            self.tasks[task_id]["result"] = f.read()

    def parse_website(self, url: str, max_depth: int = 3):
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {"status": "pending", "progress": 0, "result": None}
        asyncio.run(self.crawl_website(url, max_depth, task_id))
        return task_id

    def get_task_status(self, task_id: str):
        return self.tasks.get(task_id, {"status": "not_found", "progress": 0, "result": None})

parser = WebsiteParser()