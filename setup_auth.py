# setup_auth.py
import time
from playwright.sync_api import sync_playwright
import os
import getpass

def setup_authentication():
    AUTH_FILE = "auth/auth_state.json"
    # 현재 로그인된 Windows 사용자 이름을 가져와 경로를 완성합니다.
    username = getpass.getuser()
    user_data_dir = f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data"

    if not os.path.exists(user_data_dir):
        print(f"❌ Chrome 사용자 프로필 경로를 찾을 수 없습니다: {user_data_dir}")
        print("Chrome이 기본 경로에 설치되었는지 확인해주세요.")
        return

    with sync_playwright() as p:
        # 사용자님의 실제 Chrome 프로필을 사용하여 브라우저 컨텍스트를 실행합니다.
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            # channel="chrome" # 로컬에 설치된 실제 Chrome을 사용하도록 지정
        )
        page = context.new_page()

        print("="*60)
        print("사용자님의 실제 Chrome 브라우저와 연결되었습니다.")
        print("트위터(X)에 이미 로그인되어 있는지 확인합니다...")
        print("="*60)
        
        try:
            page.goto("https://x.com/home")
            # 타임라인이 보이는지 30초간 확인하여 로그인 상태를 체크합니다.
            page.wait_for_selector("article[data-testid='tweet']", timeout=30000)
            print("\n[성공] 이미 로그인된 상태입니다. 인증 파일을 저장합니다.")

        except Exception:
            print("\n[알림] 자동 로그인이 확인되지 않았습니다.")
            print("5분 안에 직접 로그인 또는 인증을 완료해주세요.")
            page.goto("https://x.com/login")
            time.sleep(300) # 5분 대기

        # 현재 로그인 상태를 파일로 저장
        os.makedirs("auth", exist_ok=True)
        context.storage_state(path=AUTH_FILE)
        
        print(f"\n[성공] 로그인 상태를 '{AUTH_FILE}' 파일로 저장했습니다.")
        context.close()

if __name__ == "__main__":
    setup_authentication()