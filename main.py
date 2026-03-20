import threading
from collectors.darkweb_spyder_v2 import ForumMonitor

def memory_parser(url, raw_html):
    print("=" * 50)
    print(f"🎯 [수집 완료] {url}")
    print(f"📦 [HTML 크기] {len(raw_html)} bytes")
    print(f"📝 [미리보기] {raw_html[:200]}...") # 앞부분 200글자만 잘라서 보여줌
    print("=" * 50 + "\n")

def run_bot(config):
    bot = ForumMonitor(target_config=config, callback=memory_parser)

    bot.initial_full_scan(max_pages_to_scan=2) #2페이지만 스캔(테스트)

    bot.start_monitoring(check_interval=10) #10초 주기로 모니터링

if __name__ == "__main__":
    
    dark_config = {
        "name" : "darkForum",
        "type" : "dark",
        "use_tor" : False,
        "domain" : "https://darkforums.su",
        "base_url" : "https://darkforums.su/Forum-Databases",
        
    }

    thread1 = threading.Thread(target=run_bot, args=(dark_config,))
    thread1.start()
