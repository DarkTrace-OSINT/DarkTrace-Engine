from pydantic import BaseModel, Field, ConfigDict
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
    model_config = ConfigDict(frozen=True)

    site_id: int
    raw_text: str
    collected_at: datetime = Field(default_factory=datetime.now)
    
 


class ParsedThreatData(BaseModel):
    model_config = ConfigDict(frozen=True)

    raw_id: int = 0
    leak_title: Optional[str] = None
    clean_content: str  
    structured_json: Dict[str, Any] = Field(default_factory=dict)
    parsed_at: datetime = Field(default_factory=datetime.now)
    
 

    def to_api_format(self, site_id: int) -> dict:
        
        return {
            "siteId": site_id,
            "rawText": self.clean_content,  
            "collectedAt": self.parsed_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class EngineStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    site_id: int
    source_name: str
    crawler_status: CrawlerStatus = CrawlerStatus.ALIVE
    

    def to_api_format(self) -> dict:
        return {
            "siteId": self.site_id,
            "sourceName": self.source_name,
            "crawlerStatus": self.crawler_status.value
        }


class ParsingError(Exception):
    
    pass
