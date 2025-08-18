# main.py
import os
from playwright.sync_api import sync_playwright
from scraper import Scraper
from reporter import save_reports
from config import AUTH_FILE, SCREENSHOTS_DIR

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # 로그인 상태가 있으면 사용, 없으면 일반 컨텍스트 사용
        if os.path.exists(AUTH_FILE):
            print(f"[알림] '{AUTH_FILE}' 파일을 사용하여 로그인 상태로 실행합니다.")
            context = browser.new_context(storage_state=AUTH_FILE)
        else:
            print(f"[경고] '{AUTH_FILE}' 파일이 없어 로그아웃 상태로 실행합니다.")
            context = browser.new_context()
            
        page = context.new_page()
        
        # 스크린샷 폴더 생성
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
        
        try:
            scraper = Scraper(page)
            
            # 1단계: 키워드 발굴
            keywords = scraper.extract_keywords()
            
            # 2단계: 심층 검색
            results = scraper.search_sites(keywords)
            
            # 3단계: 리포트 생성
            save_reports(keywords, results)
            
        except Exception as e:
            print(f"\n[오류] 메인 프로세스 실행 중 오류 발생: {e}")
            page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "main_error.png"))
        finally:
            context.close()
            browser.close()
            print("\n[알림] 트렌드 리서치 V3 실행이 완료되었습니다.")

if __name__ == "__main__":
    main()
