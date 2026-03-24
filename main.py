import threading
from collectors.darkweb_spyder_v2 import DarkwebSpyder

def memory_parser(url, raw_html, site_id=1): # site_id를 인자로 받게 수정
    print("=" * 50)
    print(f" [수집 완료] {url}")
    print(f" [HTML 크기] {len(raw_html)} bytes")

    try:
        # 1. Raw 데이터 객체 생성
        raw_data = RawCollectedData(
            site_id=site_id,
            raw_text=raw_html
        )

        # 2. 파서 실행 (HTML -> 가공된 텍스트)
        parser = DataParser(site_id=site_id)
        parsed = parser.parse_html(raw_data)

        # 3. 결과 확인용 출력
        print(f" [파싱 성공] 제목: {parsed.leak_title}")
        print(f" [파싱 성공] 본문 길이: {len(parsed.clean_content)}")

        # 4. API 전송용 데이터 생성 (여기에 나중에 requests.post 넣으면 끝!)
        api_data = parsed.to_api_format(site_id=site_id)

        return api_data

    except Exception as e:
        print(f" ❌ 파싱 실패 ({url}): {e}")
        return None

    print("=" * 50 + "\n")

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
