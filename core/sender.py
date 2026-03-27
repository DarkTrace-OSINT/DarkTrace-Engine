import requests
import os
import logging
from datetime import datetime
from config.settings import API_BASE_URL, API_INGESTION_KEY
from core.schemas import EngineStatus, CrawlerStatus

logger = logging.getLogger("DarkTrace_Sender")



class DataSender:
    def __init__(self):
        self.base_url = API_BASE_URL.rstrip('/')
        self.session = requests.Session()

        self.session.headers.update({
            "ngrok-skip-browser-warning": "69420",
            "Content-Type": "application/json",
            "X-API-KEY": API_INGESTION_KEY,
            
        })

    def send_raw_data(self, site_id: int, title: str, indicator_value: str, source_name: str, raw_text: str) -> bool:      
        url = os.getenv("NGROK_INGESTION_URL")
        payload = {
            "siteId": site_id,
            "title": title, 
            "indicatorValue": indicator_value, 
            "sourceName": source_name,
            "rawText": raw_text[:5000],
            "collectedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            resp = self.session.post(url, json=payload, timeout=30)

            try:
                resp_json = resp.json()
            except ValueError:
                resp_json = {}

            if resp.status_code == 200 and resp_json.get("code") == "SUCCESS":
                return True
            else:
                logger.warning(f"[API 8번 전송 실패] 서버 응답 코드: {resp.status_code}")
                return False
            
        
        except Exception as e:
            logger.error(f"[API 8번 연결 에러] 백엔드 연결 불가: {e}")
            return False
        
    def send_engine_status(self, site_id: int, source_name: str, status: str = "ALIVE") -> bool:
        
        url = f"{self.base_url}/api/v1/system/engines"
        engine_stat = EngineStatus(
            site_id=site_id, 
            source_name=source_name, 
            crawler_status=CrawlerStatus(status)
        )
        
        payload = {"engines": [engine_stat.to_api_format()]}
        
        try:
            resp = self.session.post(url, json=payload, timeout=5)
            if resp.status_code != 200:
                logger.warning(f"[API 6번 신고 실패] 서버 응답 코드: {resp.status_code}")
                return False
            return True
            
        except Exception:
            return False