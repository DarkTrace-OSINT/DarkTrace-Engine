import os
import json
from dotenv import load_dotenv

#load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

TOR_PROXY_URL = os.getenv("TOR_PROXY_URL", "socks5h://127.0.0.1:9050")

try:
    _cookies_raw = os.getenv("SECRET_COOKIES_JSON", "{}")
    TARGET_COOKIES = json.loads(_cookies_raw)
except Exception as e:
    print(f"⚠️ [.env 로드 에러] 쿠키 JSON 형식이 잘못되었습니다: {e}")
    TARGET_COOKIES = {}

