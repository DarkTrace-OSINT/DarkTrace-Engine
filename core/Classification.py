import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_INGESTION_KEY")

def send_to_ingestion_api(parsed_data):
    url = "https://unpercipient-woodrow-nonrecurent.ngrok-free.dev/api/v1/ingestion/raw"
    
    content_str = (
        f"ID: {parsed_data.get('username')} | "
        f"Email: {parsed_data.get('email')} | "
        f"PW: {parsed_data.get('password')}"
    )
    payload = {
        "siteId": 1,
        "rawText": content_str,
        "collectedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': API_KEY 
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status: {response.status_code}, Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")


sample_data = {
    "username": "gmatt",
    "email": "2094946036@qq.com",
    "password": "$2a$10$qfr.tu0V3LSnaPjhBrnZ5O..."
}

send_to_ingestion_api(sample_data)