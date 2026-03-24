import requests
import json
from datetime import datetime

# [8번] API 서버 주소 (실제 주소로 수정 필요)
API_URL = "http://서버아이피:포트/api/v1/ingestion/raw"

def send_to_server(user_id, user_email, user_pw):
    """류재연(4번)이 분석한 규격으로 데이터를 포장해서 전송하는 함수"""
    payload = {
        "siteId": 1,
        "rawText": f"ID: {user_id} | Email: {user_email} | PW: {user_pw}", # 2번 분석 내용 반영
        "collectedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        response = requests.post(API_URL, json=payload)
        print(f"📡 [서버 전송] 상태: {response.status_code}")
    except Exception as e:
        print(f"❌ [전송 실패] 에러: {e}")
import threading
from collectors.darkweb_spyder_v2 import DarkwebSpyder
from processors.parser import DataParser
from core.schemas import RawCollectedData

def memory_parser(url, raw_html):
    print(f"📥 데이터 분석 시작: {url}")

    try:
        # 1. 텍스트를 JSON 객체로 변환
        import json
        data = json.loads(raw_html)
        
        # 2. 질문자님이 분석한 '키(Key)'를 이용해 값 추출
        source = data.get("_source", {})
        u_id = source.get("username", "N/A")    # ID 추출
        u_email = source.get("email", "N/A")   # Email 추출
        u_pw = source.get("password", "N/A")    # PW 추출 (BCrypt 해시)

        # 3. 분석된 데이터를 출력 (확인용)
        print(f"✅ 분석 완료 - ID: {u_id}, Email: {u_email}")
        
        # 상단에 정의해둔 전송 함수 호출
        send_to_server(u_id, u_email, u_pw)

    except Exception as e:
        print(f"❌ [4번 역할 오류] 데이터 분석 중 에러 발생: {e}")
def run_spider():
    print("엔진 시작")

    spyder = DarkwebSpyder(callback=memory_parser)

    targets = spyder.fetch_github_target()
    if not targets:
        print("타겟 없음")
        return
    
    print(f"[*] 확보된 Online 타겟: {len(targets)}개\n")
    for target in targets[:3]: 
        domain = target["domain"]
        print(f"[+] 타겟 분석 시작: {target['name']} ({domain})")
        
        spyder.setup_target(domain, target["is_onion"])
        board_url = spyder.find_target_board(target["base_url"], domain)

        if not board_url:
            print(f"  ⏭️ [Skip] 유효한 게시판을 찾지 못해 건너뜁니다.\n")
            continue

        print(f"  🎯 타겟 게시판 확정: {board_url}")

        spyder.scrape_board(board_url, target["domain"])


if __name__ == "__main__":
    t = threading.Thread(target=run_spider)
    t.start()
    t.join()
