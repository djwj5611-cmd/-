# save_cookies.py
import time
from playwright.sync_api import sync_playwright

def save_auth_state():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) # 직접 로그인할 수 있도록 브라우저 실행
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://x.com/login")
        print("="*50)
        print("브라우저가 열렸습니다. 5분 안에 직접 로그인하세요.")
        print("로그인이 완료되면 브라우저를 닫지 말고 기다려주세요.")
        print("="*50)

        time.sleep(300)  # 5분 동안 로그인 대기

        # 현재 로그인 상태 (쿠키, 로컬 스토리지 등)를 파일로 저장
        context.storage_state(path="auth.json")
        
        print("\n[성공] 로그인 상태를 'auth.json' 파일로 저장했습니다.")
        browser.close()

if __name__ == "__main__":
    save_auth_state()