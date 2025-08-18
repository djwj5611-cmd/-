# setup_auth.py
import time
import os
import getpass
import subprocess
from playwright.sync_api import sync_playwright

def kill_chrome_processes():
    """기존에 실행 중인 모든 Chrome 프로세스를 강제 종료합니다."""
    try:
        print("[알림] 기존 Chrome 프로세스를 모두 종료합니다...")
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], check=True, capture_output=True, text=True)
        print("[성공] Chrome 프로세스 종료 완료.")
        time.sleep(2)
    except subprocess.CalledProcessError as e:
        if "프로세스를 찾을 수 없습니다" in e.stderr:
            print("[정보] 실행 중인 Chrome 프로세스가 없습니다.")
        else:
            print(f"[경고] Chrome 프로세스 종료 중 오류 발생: {e.stderr}")
    except FileNotFoundError:
        print("[경고] taskkill 명령어를 찾을 수 없습니다. 수동으로 Chrome을 종료해주세요.")

def setup_authentication():
    AUTH_FILE = "auth/auth_state.json"
    username = getpass.getuser()
    # 문자열을 Raw String (r"...")으로 변경하여 백슬래시 문제를 해결합니다.
    user_data_dir = rf"C:\Users\{username}\AppData\Local\Google\Chrome\User Data"
    
    executable_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    if not os.path.exists(executable_path):
        executable_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        if not os.path.exists(executable_path):
            print(f"❌ 정식 Chrome 브라우저를 찾을 수 없습니다. 경로: {executable_path}")
            return

    if not os.path.exists(user_data_dir):
        print(f"❌ Chrome 사용자 프로필 경로를 찾을 수 없습니다: {user_data_dir}")
        return

    kill_chrome_processes()

    with sync_playwright() as p:
        print(f"[알림] 다음 경로의 Chrome 브라우저를 실행합니다: {executable_path}")
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            executable_path=executable_path
        )
        page = context.new_page()

        print("="*60)
        print("사용자님의 실제 정식 Chrome 브라우저와 연결되었습니다.")
        print("트위터(X)에 이미 로그인되어 있는지 확인합니다...")
        print("="*60)
        
        try:
            page.goto("https://x.com/home")
            page.wait_for_selector("article[data-testid='tweet']", timeout=30000)
            print("\n[성공] 이미 로그인된 상태입니다. 인증 파일을 저장합니다.")
        except Exception:
            print("\n[알림] 자동 로그인이 확인되지 않았습니다.")
            print("5분 안에 직접 로그인 또는 인증을 완료해주세요.")
            page.goto("https://x.com/login")
            time.sleep(300)

        os.makedirs("auth", exist_ok=True)
        context.storage_state(path=AUTH_FILE)
        
        print(f"\n[성공] 로그인 상태를 '{AUTH_FILE}' 파일로 저장했습니다.")
        context.close()

if __name__ == "__main__":
    setup_authentication()