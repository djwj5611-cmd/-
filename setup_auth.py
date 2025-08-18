# setup_auth.py
import time
import os
import getpass
from playwright.sync_api import sync_playwright

# 설정
SITES = {
    "twitter": "https://x.com/login",
    "naver": "https://nid.naver.com/nidlogin.login",
    "google": "https://accounts.google.com"
}
AUTH_DIR = "auth"

def setup_authentication(site_name):
    if site_name not in SITES:
        print(f"❌ 지원하지 않는 사이트입니다: {site_name}. (지원 목록: {list(SITES.keys())})")
        return

    AUTH_FILE = os.path.join(AUTH_DIR, f"{site_name}_auth.json")
    login_url = SITES[site_name]
    
    username = getpass.getuser()
    user_data_dir = rf"C:\Users\{username}\AppData\Local\Google\Chrome\User Data"
    executable_path = "C:\Program Files\Google\Chrome\Application\chrome.exe"

    if not os.path.exists(executable_path):
        executable_path = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(executable_path):
        print("❌ Chrome 브라우저를 찾을 수 없습니다.")
        return

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            executable_path=executable_path
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("="*60)
        print(f"'{site_name.upper()}' 사이트의 로그인을 시작합니다.")
        print("5분 안에 로그인을 완료하고, 창을 닫지 말고 기다려주세요.")
        print("="*60)
        
        page.goto(login_url, timeout=60000)
        time.sleep(300) # 5분 대기

        os.makedirs(AUTH_DIR, exist_ok=True)
        context.storage_state(path=AUTH_FILE)
        
        print(f"\n[성공] '{site_name}' 로그인 상태를 '{AUTH_FILE}' 파일로 저장했습니다.")
        context.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("사용법: python setup_auth.py [사이트 이름]")
        print(f"예시: python setup_auth.py twitter")
    else:
        site_to_setup = sys.argv[1].lower()
        setup_authentication(site_to_setup)
