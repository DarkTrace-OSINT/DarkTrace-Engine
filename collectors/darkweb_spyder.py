import os
import time
import json
import requests
from dotenv import load_dotenv
from collectors.common_utils import DarkwebParser
from core.schemas import DarkwebDataDTO, CollectorError, ParsingError

load_dotenv()


TOR_PROXY_URL = os.getenv("TOR_PROXY_URL", "socks5h://127.0.0.1:9050")


class DarkWebSpyder:
    def __init__(self):
        
        self.parser = DarkWebParser()

        self.session = requests.Session()

        self.session.proxies = {
            "http" : TOR_PROXY_URL, "https" : TOR_PROXY_URL
        }

        self.session.headers.update({
            "User-Agent" : self.parser.get_random_user_agent()
        })

        self.visited = set()
        self.to_visit = []



        def get_page(self):
            try:
                resp = self.session.get(url, timeout=60)

                resp.raise_for_status()

                resp.encoding = resp.apparent_encoding or 'utf-8'

                return resp.text
            
            except requests.exceptions.RequestException as e:
                site_domain = url.split('/')[2] if '//' in url else url

                error_log = {
                    "error_code": "E001",
                    "site_id": site_domain,
                    "message": "Tor Network connection failure or timeout : {}".format({str(e)})
                }

                print(json.dumps(error_log, ensure_ascii=False))

                raise CollectorError(error_log["message"])

        def run(self, seed_url, max_page=5):

            self.to_visit.append(seed_url)

            collected_boxes=[]

            while self.to_visit and len(self.visited) < max_page:

                current_url = self.to_visit.pop(0).strip()

                if not current_url or current_url in self.visited:
                    continue

                try:

                    html = self.get_page(current_url)
                    self.visited.add(current_url)

                    if html:
                        try:

                            artifacts = self.parser.extract_artifacts(html)

                            page_title = self.parser.parse_page_title(html)
                            
                        except Exception as e:

                            site_domain = current_url.split('/')[2]

                            error_log = {
                                "error_code": "E002",
                                "site_id": site_domain,
                                "message": "HTML parsing failed : {}".format({str(e)})
                            }
                            print(json.dumps(error_log, ensure_ascii=False))

                            raise  ParsingError(error_log["message"])

                        for link in artifacts.get("onion_links", []):
                            if link not in self.visited and link not in self.to_visit:
                                self.to_visit.append(link)

                        dto = DarkwebDataDTO(
                            site_id=current_url.split('/')[2], 
                            url=current_url,
                            title=page_title,
                            emails=artifacts["emails"],
                            btc_addresses=artifacts["btc_addresses"],
                            has_indicators=artifacts["has_indicators"],
                            text_length=len(html),
                            indicator_count=len(artifacts["emails"]) + len(artifacts["btc_addresses"])
                        )

                        collected_boxes.append(dto)
                
                except(CollectorError, ParsingError):
                    continue

                time.sleep(3)
            
            return collected_boxes


        

        
