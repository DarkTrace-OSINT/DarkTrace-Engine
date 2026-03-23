"""
processors/parser.py
HTML 파싱 로직
"""

from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, List, Dict, Any, Generator
import re
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.schemas import RawCollectedData, ParsedThreatData, ParsingError


class DataParser:
    """HTML 파서"""
    
    def __init__(self, site_id: int):
        self.site_id = site_id
        self.leak_keywords = [
            'database', 'leak', 'dump', 'breach', 'combo',
            'password', 'email', 'credential', 'account', 'records'
        ]
    
    def parse_html(self, raw_data: RawCollectedData) -> ParsedThreatData:
        """HTML -> ParsedThreatData"""
        
        try:
            soup = BeautifulSoup(raw_data.raw_text, 'html.parser')
            
            title = self._extract_title(soup)
            author = self._extract_author(soup)
            date = self._extract_date(soup)
            content = self._extract_content(soup)
            indicators = self._extract_indicators(soup.get_text())
            
            text_length = len(raw_data.raw_text)
            keyword_count = self._count_keywords(soup.get_text())
            
            structured_json = {
                "title": title,
                "author": author,
                "date": date,
                "content_preview": content[:500] if content else None,
                "indicators": indicators,
                "stats": {
                    "text_length": text_length,
                    "keyword_count": keyword_count,
                    "indicator_count": sum(len(v) for v in indicators.values()),
                },
                "keywords_found": self._find_keywords(soup.get_text()),
            }
            
            return ParsedThreatData(
                raw_id=0,
                leak_title=title,
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
        return None
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        for selector in ['a.username', '.message-name a', '.username']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return None
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        elem = soup.select_one('time[datetime]')
        return elem.get('datetime') if elem else None
    
    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        for selector in ['.message-body .bbWrapper', '.message-body', '.bbWrapper']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return None
    
    def _extract_indicators(self, text: str) -> Dict[str, List[str]]:
        indicators = {"emails": [], "phones": [], "ips": []}
        
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        indicators["emails"] = list(set(emails))[:50]
        
        phones = re.findall(r'01[0-9]-?\d{4}-?\d{4}', text)
        indicators["phones"] = list(set(phones))[:50]
        
        ips = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', text)
        indicators["ips"] = list(set(ips))[:50]
        
        return indicators
    
    def _count_keywords(self, text: str) -> int:
        text_lower = text.lower()
        return sum(text_lower.count(kw) for kw in self.leak_keywords)
    
    def _find_keywords(self, text: str) -> List[str]:
        text_lower = text.lower()
        return [kw for kw in self.leak_keywords if kw in text_lower]
