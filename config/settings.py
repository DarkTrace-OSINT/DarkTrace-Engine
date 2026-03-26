import os
import json
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

TOR_PROXY_LIST = [f"socks5h://127.0.0.1:{port}" for port in range(9050, 9060)]

TARGET_LIST_URL = os.getenv("TARGET_LIST_URL")
API_BASE_URL = os.getenv("API_BASE_URL")
API_INGESTION_KEY = os.getenv("API_INGESTION_KEY")

