import os
import time
import logging
import requests
import random
import re
import json
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from config.settings import TOR_PROXY_LIST, TARGET_LIST_URL

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'spider_error.log')

os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("DarkwebSpyder")
logger.setLevel(logging.ERROR)
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class DarkwebSpyder:
    def __init__(self, callback=None):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/115.0"})
        self.seen_urls = set()
        self.callback = callback

        self.max_seen_urls = 10000
        self.sleep_min = 0.1
        self.sleep_max = 0.5

    def _log_error (self, error_code, site_id, message):
        error_data = {
            "error_code": error_code,
            "site_id": site_id,
            "message": message
        }
        print(f"[ERROR] {message}")
        logger.error(json.dumps(error_data, ensure_ascii=False))

    def setup_target(self, domain, is_onion):
        self.session.cookies.clear()
        if is_onion:
            selected_proxy = random.choice(TOR_PROXY_LIST)
            self.session.proxies = {"http": selected_proxy, "https": selected_proxy}
        
        else:
            self.session.proxies = {}

    def fetch_github_target(self):
        try:
            resp = self.session.get(TARGET_LIST_URL, timeout=30)
            resp.raise_for_status()

            target_list = []
            seen_domain = set()


            for line in resp.text.splitlines():
                
                if "online" in line.lower():
                    
                    match = re.search(r"\[(.*?)\]\((.*?)\)", line)
                    
                    if match:
                        name = match.group(1).strip()
                        forum_url = match.group(2).strip()
                        
                        if forum_url.startswith("http"):

                            parsed_url = urlparse(forum_url)
                            domain = parsed_url.netloc.lower()


                            domain = domain.split(':')[0]
                            if domain.startswith("www."):
                                domain = domain[4:]


                            if not domain or domain in seen_domain:
                                continue
                            
                            seen_domain.add(domain)

                            target_list.append({
                                "name" : name,
                                "base_url" : forum_url,
                                "domain" : domain,
                                "is_onion" : ".onion" in domain
                            })
                            
            return target_list
            
        except Exception as e:
            self._log_error("E000", "GitHub", f"타겟 리스트 갱신 실패 : {str(e)}")
            return []
        
    def is_login_wall(self, html):
        if not html: return True
        html_lower = html.lower()
        if "you must be logged in" in html_lower or "register to view" in html_lower or len(html) < 2000:
            return True
        return False
    
    def find_target_board(self, base_url, domain):
        try:
            resp = self.session.get(base_url, timeout=45)
            html = resp.text
            if self.is_login_wall(html): return None

            soup = BeautifulSoup(html, 'html.parser')
            keywords = ['database', 'leak', 'dump', 'breach']
            
            for a_tag in soup.find_all('a', href=True):
                href, text = a_tag['href'].lower(), a_tag.text.lower()
                if any(kw in href or kw in text for kw in keywords):
                    if 'action=lastpost' in href or 'unread' in href: continue
                    return href if href.startswith('http') else urljoin(base_url, a_tag['href'])
            return None
        except Exception as e:
            self._log_error("E001", domain, f"메인 접속 실패: {str(e)}")
            return None

    def _extract_post_links(self, html, board_url):
            soup = BeautifulSoup(html, 'html.parser')
            new_posts = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                if ('/threads/' in href) or (href.startswith('Thread-')):
                    if 'unread' in href or 'latest' in href or '#' in href: continue
                    
                    clean_link = href if href.startswith('http') else urljoin(board_url, href)
                    new_posts.append(clean_link)
            return list(set(new_posts))      


    def scrape_board(self, board_url, domain):
        try:
            resp = self.session.get(board_url, timeout=45)
            html = resp.text

            
            post_links = self._extract_post_links(html, board_url)
            if not post_links:
                return
            
            if len(self.seen_urls) > self.max_seen_urls:
                self.seen_urls.clear()

            for post_url in post_links:
                if post_url not in self.seen_urls:
                    self.seen_urls.add(post_url)
                    try:
                        
                        post_resp = self.session.get(post_url, timeout=45)
                        post_html = post_resp.text

                        if self.callback and post_html:
                            self.callback(domain, post_url, post_html)

                        time.sleep(random.uniform(self.sleep_min, self.sleep_max))
                    except Exception as inner_e:
                        self._log_error("E003", domain, f"개별 게시글 수집 실패 ({post_url}): {str(inner_e)}")
                        continue
        except Exception as e:
            self._log_error("E002", domain, f"게시판 스크래핑 실패: {str(e)}")

    def send_to_backend(self, post_url, domain, html):
            
            target_url = os.getenv("NGROK_INGESTION_URL")

            soup = BeautifulSoup(html, 'html.parser')
            page_title = soup.title.string.strip() if soup.title and soup.title.string else "제목 없음"

            headers = {
                "ngrok-skip-browser-warning": "69420",
                "X-API-KEY": os.getenv("API_INGESTION_KEY"),
                "Content-Type": "application/json"
            }
            
            payload = {
                "siteId": 1,
                "title": page_title, 
                "indicatorValue": post_url,
                "sourceName": domain,
                "rawText": html[:5000], 
                "collectedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            try:
                
                response = requests.post(target_url, json=payload, headers=headers, timeout=30)
                if response.status_code == 200:
                    print("전송 성공")
                else:
                    print(f"전송 실패 (상태 코드: {response.status_code})")
            except Exception as e:
                print(f"전송 에러: {e}")

                


                
