import requests
import json
from datetime import datetime

def send_to_ingestion_api(parsed_data):
    # 1. 서버 주소 설정 (이미지 8번 API 엔드포인트)
    url = "http://서버주소:포트/api/v1/ingestion/raw"
    
    # 2. 4번 역할(류재연)이 분석한 필드를 JSON 문자열로 변환
    # 샘플 데이터에서 뽑은 ID, Email, PW 등을 하나의 텍스트로 합칩니다.
    content_str = (
        f"ID: {parsed_data.get('username')} | "
        f"Email: {parsed_data.get('email')} | "
        f"PW: {parsed_data.get('password')}"
    )

    # 3. 가이드에 적힌 JSON Body 구성
    payload = {
        "siteId": 1,                      # BreachForums 등 사이트 번호
        "rawText": content_str,            # 분석한 텍스트 데이터
        "collectedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # 4. 전송
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            print("✅ [성공] 데이터가 서버로 전송되었습니다.")
        else:
            print(f"❌ [실패] 서버 응답 코드: {response.status_code}")
    except Exception as e:
        print(f"❌ [에러] 서버 연결 불가: {e}")

# 실행 예시 (분석한 샘플 데이터 적용)
sample_from_4번 = {
    "username": "gmatt",
    "email": "2094946036@qq.com",
    "password": "$2a$10$qfr.tu0V3LSnaPjhBrnZ5O..."
}

send_to_ingestion_api(sample_from_4번)
