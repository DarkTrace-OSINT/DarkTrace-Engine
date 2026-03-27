import threading
import time
import json
import logging
import os
from datetime import datetime
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from collectors.darkweb_spyder_v2 import DarkwebSpyder
from core.sender import DataSender
from core.schemas import RawCollectedData
from processors.parser import DataParser


logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("DarkTrace_Main")

DEFAULT_SITE_ID = 1
MAX_WORKERS = 30
HEARTBEAT_INTERVAL = 300


total_scraped_count = 0
counter_lock = threading.Lock()
api_sender = DataSender()


def memory_parser(domain, url, raw_html):
    global total_scraped_count
    with counter_lock:
        total_scraped_count += 1

    try:
        soup = BeautifulSoup(raw_html, 'html.parser')
        page_title = soup.title.string.strip() if soup.title and soup.title.string else "제목 없음"
    except:
        page_title = "제목 없음"
        
    try:
        data = json.loads(raw_html)
        source = data.get("_source", {})
        u_id = source.get("username", "N/A")    
        u_email = source.get("email", "N/A")   
        u_pw = source.get("password", "N/A")    

        formatted_text = f"ID: {u_id} | Email: {u_email} | PW: {u_pw}"

        api_sender.send_raw_data(
            site_id=DEFAULT_SITE_ID, 
            title=page_title, 
            indicator_value=url, 
            source_name=domain, 
            raw_text=formatted_text
        )

        if total_scraped_count % 100 == 0:
            logger.info(f"누적 {total_scraped_count}개 수집 및 전송 완료")
    
    except json.JSONDecodeError:
       
        try:
            raw_data = RawCollectedData(site_id=DEFAULT_SITE_ID, raw_text=raw_html)
            parser = DataParser(site_id=DEFAULT_SITE_ID)

            parsed_data = parser.parse_html(raw_data)

            api_sender.send_raw_data(
                site_id=DEFAULT_SITE_ID, 
                title=page_title, 
                indicator_value=url, 
                source_name=domain, 
                raw_text=parsed_data.clean_content
            )
        except Exception as parse_e:
            logger.error(f"HTML 파싱 오류 ({url}): {parse_e}")

            api_sender.send_raw_data(
                site_id=DEFAULT_SITE_ID, 
                title=page_title, 
                indicator_value=url, 
                source_name=domain, 
                raw_text=raw_html
            )

        if total_scraped_count % 100 == 0:
            logger.info(f"누적 {total_scraped_count}개 수집 및 정제 전송 완료")


def process_target(target):
    spyder = DarkwebSpyder(callback=memory_parser) 
    domain = target["domain"]
    
    try:
        spyder.setup_target(domain, target["is_onion"])
        board_url = spyder.find_target_board(target["base_url"], domain)

        if board_url:
            spyder.scrape_board(board_url, domain)

    except Exception as e:
        logger.error(f"타겟 처리 실패 ({domain}): {e}")
    finally:
        spyder.session.close()


def heartbeat_daemon():
    while True:
        api_sender.send_engine_status(site_id=DEFAULT_SITE_ID, source_name="DarkTrace_Main", status="ALIVE")
        time.sleep(HEARTBEAT_INTERVAL)


def run_spider():
    logger.info("오픈데이터 수집 시작")
    
    master_spyder = DarkwebSpyder()
    targets = master_spyder.fetch_github_target()

    if not targets:
        logger.warning("타겟을 찾을 수 없습니다. (GitHub 리스트 확인)")
        return
    
    logger.info(f"확보된 고유 타겟: {len(targets)}개 ({MAX_WORKERS}개 스레드 투입)")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_target, target) for target in targets]
        for future in as_completed(futures):
            try:
                future.result() 
            except Exception:
                pass
                
    logger.info("모든 타겟 스캔 완료. 엔진 대기 모드 진입.")

if __name__ == "__main__":
    daemon_thread = threading.Thread(target=heartbeat_daemon, daemon=True)
    daemon_thread.start()

    try:
        while True: 
            logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 새 수집 사이클을 시작")
            run_spider() 
            logger.info("모든 타겟 스캔 완료. 10분간 sleep 후 다시 시작")
            time.sleep(600)

    except KeyboardInterrupt:
        logger.warning("사용자에 의해 스캔이 강제 종료되었습니다")
        api_sender.send_engine_status(site_id=DEFAULT_SITE_ID, source_name="DarkTrace_Main", status="DEAD")
        os._exit(1)
