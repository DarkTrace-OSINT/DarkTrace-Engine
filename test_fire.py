import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# 1. 환경변수 로드
load_dotenv()
target_url = os.getenv("NGROK_INGESTION_URL")
api_key = os.getenv("API_INGESTION_KEY")

now = datetime.now()
time_hms = now.strftime("%H:%M:%S")

# 2. 팀장님이 요청한 "정규식 테스트용" 특별 텍스트
# (이메일, IP, URL과 함께 그럴싸한 유출 계정 데이터를 하나 추가했습니다)
target_text = """유출 데이터 샘플입니다. 
관리자 이메일은 admin@darktrace.com 이고, 
서버 IP는 192.168.0.1 입니다. 
출처는 https://kali-test.onion/ 입니다.

[유출 데이터 1건]
Username: ceo_admin
Password: SuperSecretPassword2026!
"""

# 3. 데이터 포장
payload = {
    "siteId": 1,
    "title": "[TEST] 백엔드 정규식 파싱 엔진 테스트", 
    "indicatorValue": "https://kali-test.onion/",
    "sourceName": "kali-test.onion",
    "rawText": target_text,
    "collectedAt": now.strftime("%Y-%m-%d %H:%M:%S")
}

headers = {
    "ngrok-skip-browser-warning": "69420",
    "X-API-KEY": api_key,
    "Content-Type": "application/json"
}

print(f"🎯 목적지: {target_url}")
print("🚀 정규식 테스트용 포탄 장전 완료. 발사!")

try:
    response = requests.post(target_url, json=payload, headers=headers, timeout=10)
    
    print(f"\n🎯 [서버 응답 결과]")
    print(f"서버 응답 내용: {response.text}") 
    
    if response.status_code == 200 and "SUCCESS" in response.text:
        print("\n✅ [전송 성공] 백엔드 파싱 엔진으로 데이터가 무사히 넘어갔습니다!")
        print("-" * 50)
        print(f"📢 팀장님께 복사해서 보내드릴 시간: {time_hms}")
        print("-" * 50)
    else:
        print("\n❌ 전송 실패")
        
except Exception as e:
    print(f"\n🚨 에러 발생: {e}")
