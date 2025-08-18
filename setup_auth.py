# setup_auth.py (Final Copy-Only Version)
import os
import getpass
import subprocess
import time
from playwright.sync_api import sync_playwright

SITES = ["twitter", "naver", "google"]
AUTH_DIR = "auth"

def kill_chrome_processes():
    """기존에 실행 중인 모든 Chrome 프로세스를 강제 종료합니다."""
    try:
        print("[알림] 기존 Chrome 프로세스를 모두 종료합니다...")
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], check=True, capture_output=True, text=True)
        print("[성공] Chrome 프로세스 종료 완료.")
        time.sleep(2)
    except Exception:
        print("[정보] 실행 중인 Chrome 프로세스가 없거나 종료할 수 없습니다.")

def setup_authentication(site_name):
    if site_name not in SITES:
        print(f"❌ 지원하지 않는 사이트입니다: {site_name}. (지원 목록: {SITES})")
        return

    AUTH_FILE = os.path.join(AUTH_DIR, f"{site_name}_auth.json")
    username = getpass.getuser()
    user_data_dir = rf"C:\Users\{username}\AppData\Local\Google\Chrome\User Data"

    if not os.path.exists(user_data_dir):
        print(f"❌ Chrome 사용자 프로필 경로를 찾을 수 없습니다: {user_data_dir}")
        return

    print("="*60)
    print(f"'{site_name.upper()}' 사이트의 최신 로그인 상태를 복사합니다.")
    print("이 스크립트를 실행하기 전에, 반드시 Chrome을 열어")
    print(f"'{site_name.upper()}' 로그인을 완료한 후, 모든 Chrome 창을 닫아주세요.")
    print("="*60)
    
    kill_chrome_processes()

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(user_data_dir, headless=True)
            os.makedirs(AUTH_DIR, exist_ok=True)
            context.storage_state(path=AUTH_FILE)
            context.close()
            print(f"\n[성공] '{site_name}'의 최신 로그인 상태를 '{AUTH_FILE}' 파일로 복사했습니다.")
            
    except Exception as e:
        print(f"\n[오류] 로그인 상태 복사 중 오류: {e}")
        print("Chrome이 완전히 종료되었는지 확인 후 다시 시도해주세요.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("사용법: python setup_auth.py [사이트 이름]")
        print(f"예시: python setup_auth.py naver")
    else:
        site_to_setup = sys.argv[1].lower()
        setup_authentication(site_to_setup)