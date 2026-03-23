import threading
from collectors.darkweb_spyder_v2 import DarkwebSpyder

def memory_parser(url, raw_html):
    print("=" * 50)
    print(f"🎯 [수집 완료] {url}")
    print(f"📦 [HTML 크기] {len(raw_html)} bytes")
    print(f"📝 [미리보기] {raw_html[:200]}...") # 앞부분 200글자만 잘라서 보여줌
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
