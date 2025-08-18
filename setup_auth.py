# setup_auth.py
import time
from playwright.sync_api import sync_playwright
import os

def setup_authentication():
    AUTH_FILE = "auth/auth_state.json"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("="*60)
        print("트위터(X) 로그인을 시작합니다.")
        print("5분 안에 로그인을 완료해주세요.")
        print("="*60)
        
        page.goto("https://x.com/login")
        time.sleep(300) # 5분 대기

        # 로그인 상태 저장
        os.makedirs("auth", exist_ok=True)
        context.storage_state(path=AUTH_FILE)
        
        print(f"\n[성공] 로그인 상태를 '{AUTH_FILE}' 파일로 저장했습니다.")
        browser.close()

if __name__ == "__main__":
    setup_authentication()
