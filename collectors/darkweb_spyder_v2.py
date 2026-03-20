import os
import time
import requests
from dotenv import load_dotenv
from urllib.parse import urljoin
from bs4 import BeautifulSoup

load_dotenv()
TOR_PROXY_URL = os.getenv("TOR_PROXY_URL", "socks5h://127.0.0.1:9050")

class ForumMonitor:


    def __init__(self, target_config, callback=None):
        self.target = target_config
        self.callback = callback
        self.session = requests.Session()

        if self.target.get('use_tor',True):
            self.session.proxies = {
                "http" : TOR_PROXY_URL,
                "https" : TOR_PROXY_URL
            }

        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/115.0"})
        
        if "cookies" in self.target:
            self.session.cookies.update(self.target["cookies"])

        self.seen_urls = set()


    def assemble_url(self, page_num):

        base_url = self.target["base_url"]
        forum_type = self.target["type"]

        if page_num == 1:
            return base_url
        
        if forum_type == "breach":
            return f"{base_url.rstrip('/')}/page-{page_num}"
        
        elif forum_type == "dark":
            return f"{base_url}?page={page_num}"
        
        return base_url
    


    def get_page(self, url):

        try:
            resp = self.session.get(url, timeout=45)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f" * 접속 에러 ({url}): {e}")
            return None
        
    


    def extract_post_links(self, html):

        soup = BeautifulSoup(html, 'html.parser')
        new_posts = []
        forum_type = self.target["type"]

        for a_tag in soup.find_all('a', href=True):

            href = a_tag['href']

            if forum_type == "breach" and '/threads/' in href:

                if 'unread' in href or 'latest' in href or '#' in href:
                    continue

                clean_link = href if href.startswith('http') else urljoin(self.target["domain"], href)

                new_posts.append(clean_link)
                
            elif forum_type == "dark" and href.startswith('Thread-'):

                clean_link = urljoin(self.target["domain"], href)

                new_posts.append(clean_link)

        return list(set(new_posts))
    

    def scrape_post_html(self, post_url):
        html = self.get_page(post_url)
        if html:
            if self.callback:
                self.callback(post_url,html)
            time.sleep(2)
        return html



    def initial_full_scan(self, max_pages_to_scan=10):
        for page in range(1, max_pages_to_scan + 1):
            target_url = self.assemble_url(page)
            html = self.get_page(target_url)

            if not html:
                break

            post_links = self.extract_post_links(html)
            if not post_links:
                break

            for link in post_links:
                if link not in self.seen_urls:
                    self.seen_urls.add(link)
                    self.scrape_post_html(link)
            time.sleep(3)



    def start_monitoring(self, check_interval=300):

        while True:
            target_url = self.assemble_url(1)
            html = self.get_page(target_url)

            if html:
                new_post_links = self.extract_post_links(html)
                found_new = False

                for link in new_post_links:

                    if link not in self.seen_urls:
                        found_new = True
                        self.seen_urls.add(link)
                        self.scrape_post_html(link)

            time.sleep(check_interval)

                
