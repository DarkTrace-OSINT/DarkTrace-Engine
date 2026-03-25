from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional

from core.schemas import RawCollectedData, ParsedThreatData, ParsingError


class DataParser:

    
    def __init__(self, site_id: int):
        self.site_id = site_id

    def parse_html(self, raw_data: RawCollectedData) -> ParsedThreatData:
        
        try:
            soup = BeautifulSoup(raw_data.raw_text, 'html.parser')
            
            title = self._extract_title(soup)
            author = self._extract_author(soup)
            date = self._extract_date(soup)
            content = self._extract_content(soup)
            
            structured_json = {
                "title": title,
                "author": author,
                "date": date,
                "content_preview": content[:1000] if content else None,
                "stats": {
                    "text_length": len(raw_data.raw_text)
                }
            }
            
            full_raw_text = f"Title: {title}\nContent: {content}" if title else content
            
            return ParsedThreatData(
                raw_id=0,
                leak_title=title,
                clean_content=full_raw_text,
                structured_json=structured_json,
                parsed_at=datetime.now()
            )
            
        except Exception as e:
            raise ParsingError(f"파싱 실패: {str(e)}")
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        for selector in ['h1.p-title-value', '.p-title-value', 'h1', 'title']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return "Untitled"

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        for selector in ['a.username', '.message-name a', '.username']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return "Unknown"

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        elem = soup.select_one('time[datetime]')
        return elem.get('datetime') if elem else None

    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        for selector in ['.message-body .bbWrapper', '.message-body', '.bbWrapper']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(separator='\n', strip=True)
        return soup.get_text(separator='\n', strip=True)
