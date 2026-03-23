"""
core/schemas.py
Pydantic DTO - 팀장님 지시: frozen=True
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class ProcessStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"


class CrawlerStatus(str, Enum):
    ALIVE = "ALIVE"
    DEAD = "DEAD"
    ERROR = "ERROR"


class RawCollectedData(BaseModel):
    """3번이 주는 Raw 데이터"""
    
    site_id: int = Field(..., description="사이트 ID")
    raw_text: str = Field(..., description="HTML 등 원본 텍스트")
    collected_at: datetime = Field(default_factory=datetime.now)
    process_status: ProcessStatus = Field(default=ProcessStatus.PENDING)
    
    class Config:
        frozen = True
    
    def to_api_format(self) -> dict:
        """8번 API 형식"""
        return {
            "siteId": self.site_id,
            "rawText": self.raw_text,
            "collectedAt": self.collected_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class ParsedThreatData(BaseModel):
    """네가 만드는 가공 데이터"""
    
    raw_id: int = Field(default=0)
    leak_title: Optional[str] = None
    structured_json: Dict[str, Any] = Field(default_factory=dict)
    parsed_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        frozen = True
    
    def to_dict(self) -> dict:
        return {
            "raw_id": self.raw_id,
            "leak_title": self.leak_title,
            "structured_json": self.structured_json,
            "parsed_at": self.parsed_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class EngineStatus(BaseModel):
    """6번 API용"""
    
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
