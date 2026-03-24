import requests
import logging
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from config.settings import API_BASE_URL, API_JWT_TOKEN

logger = logging.getLogger("DarkTrace_Sender")


class RawDataPayload(BaseModel):
    model_config = ConfigDict(frozen=True)
    siteId: int
    rawText: str
    collectedAt: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class DataSender:
    def __init__(self):
        self.base_url = API_BASE_URL.rstrip('/')
        self.session = requests.Session()

        self.session.headers.update({
            "ngrok-skip-browser-warning": "69420",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_JWT_TOKEN}"
        })

    def send_raw_data(self, site_id: int, raw_text: str) -> bool:
        url = f"{self.base_url}/api/v1/ingestion/raw"
        payload = RawDataPayload(siteId=site_id, rawText=raw_text[:5000])

        try:
            resp = self.session.post(url, json=payload.model_dump(), timeout=10)
            if resp.status_code == 200:
                return True
            

            logger.warning(f"[API 8번 전송 실패] 서버 응답 코드: {resp.status_code}")
            return False
        
        except Exception as e:
            logger.error(f"[API 8번 연결 에러] 백엔드 연결 불가: {e}")
            return False
        
    def send_engine_status(self, site_id: int, source_name: str, status: str = "ALIVE") -> bool:
        
        url = f"{self.base_url}/api/v1/system/engines"
        payload = {
            "engines": [{"siteId": site_id, "sourceName": source_name, "crawlerStatus": status}]
        }
        
        try:
            resp = self.session.post(url, json=payload, timeout=5)
            if resp.status_code == 200:
                return True
                
            logger.warning(f"[API 6번 신고 실패] 서버 응답 코드: {resp.status_code}")
            return False
            
        except Exception:
            return False