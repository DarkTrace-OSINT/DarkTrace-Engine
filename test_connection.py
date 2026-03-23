"""
test_connection.py
팀원 코드(darkweb_spyder)와 파서 연결 테스트

실행: python test_connection.py
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.schemas import RawCollectedData, EngineStatus, CrawlerStatus
from processors.parser import DataParser


def memory_parser(url, raw_html):
    """팀원 코드에서 호출되는 콜백 함수"""
    
    print("\n" + "=" * 60)
    print(f"[수집 완료] {url}")
    print(f"[HTML 크기] {len(raw_html):,} bytes")
    
    raw_data = RawCollectedData(site_id=1, raw_text=raw_html)
    parser = DataParser(site_id=1)
    
    try:
        parsed_data = parser.parse_html(raw_data)
        
        print(f"[파싱 성공]")
        print(f"   제목: {parsed_data.leak_title}")
        
        sj = parsed_data.structured_json
        print(f"   작성자: {sj.get('author', 'N/A')}")
        print(f"   키워드: {sj.get('keywords_found', [])}")
        
        stats = sj.get('stats', {})
        print(f"   텍스트 길이: {stats.get('text_length', 0):,}")
        print(f"   키워드 수: {stats.get('keyword_count', 0)}")
        
        # 결과 저장
        os.makedirs('data', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/parsed_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(parsed_data.to_dict(), f, ensure_ascii=False, indent=2)
        
        print(f"[저장됨] {filename}")
        
        # 8번 API 형식 출력 (rawText는 미리보기만)
        print(f"\n[8번 API 형식] POST /api/v1/ingestion/raw")
        print("{")
        print(f'  "siteId": {raw_data.site_id},')
        print(f'  "rawText": "(HTML {len(raw_html):,} bytes - 생략)",')
        print(f'  "collectedAt": "{raw_data.collected_at.strftime("%Y-%m-%d %H:%M:%S")}"')
        print("}")
        
    except Exception as e:
        print(f"[파싱 실패] {e}")
    
    print("=" * 60)


def run_spyder_test():
    """스파이더 연결 테스트"""
    
    print("\n" + "=" * 60)
    print("    스파이더 연결 테스트")
    print("=" * 60)
    
    try:
        from collectors.darkweb_spyder_v2 import DarkwebSpyder
        
        spyder = DarkwebSpyder(callback=memory_parser)
        targets = spyder.fetch_github_target()
        
        if not targets:
            print("[오류] 타겟 없음")
            return
        
        print(f"[타겟 수] {len(targets)}개")
        
        clearnet = [t for t in targets if not t['is_onion']]
        print(f"[클리어넷] {len(clearnet)}개")
        
        success = False
        target_name = ""
        
        for i, target in enumerate(clearnet[:5]):
            print(f"\n[시도 {i+1}] {target['name']} ({target['domain']})")
            
            spyder.setup_target(target['domain'], False)
            board = spyder.find_target_board(target['base_url'], target['domain'])
            
            if board:
                print(f"[게시판 발견] {board}")
                target_name = target['name']
                spyder.scrape_board(board, target['domain'])
                success = True
                break
            else:
                print(f"[스킵] 게시판 없음")
        
        # 6번 API 형식 출력
        print("\n" + "=" * 60)
        print("[6번 API 형식] POST /api/v1/system/engines")
        print("{")
        print('  "engines": [')
        print("    {")
        print(f'      "siteId": 1,')
        print(f'      "sourceName": "{target_name if target_name else "Unknown"}",')
        print(f'      "crawlerStatus": "{"ALIVE" if success else "ERROR"}"')
        print("    }")
        print("  ]")
        print("}")
        
        if not success:
            print("\n[결과] 게시판을 찾지 못했습니다.")
        
    except ImportError:
        print("[오류] collectors/darkweb_spyder_v2.py 필요")
    except Exception as e:
        print(f"[오류] {e}")
    
    print("\n" + "=" * 60)
    print("    테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    run_spyder_test()
