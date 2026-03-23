from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class ProcessStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"


class CrawlerStatus(str, Enum):
    ALIVE = "ALIVE"
    DEAD = "DEAD"


class RawCollectedData(BaseModel):
    site_id: int
    raw_text: str
    collected_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        frozen = True


class ParsedThreatData(BaseModel):
    raw_id: int = 0
    leak_title: Optional[str] = None
    clean_content: str  # [추가] 태그가 제거된 깨끗한 텍스트
    structured_json: Dict[str, Any] = Field(default_factory=dict)
    parsed_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        frozen = True

    def to_api_format(self, site_id: int) -> dict:
        """API 8번 규격에 100% 맞춤"""
        return {
            "siteId": site_id,
            "rawText": self.clean_content,  # 정제된 텍스트 전송
            "collectedAt": self.parsed_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class EngineStatus(BaseModel):
    site_id: int
    source_name: str
    crawler_status: CrawlerStatus = CrawlerStatus.ALIVE
    
    class Config:
        frozen = True

    def to_api_format(self) -> dict:
        return {
            "siteId": self.site_id,
            "sourceName": self.source_name,
            "crawlerStatus": self.crawler_status.value
        }


class ParsingError(Exception):
    """파싱 오류"""
    pass
