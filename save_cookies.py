# save_cookies.py
import time
import pickle
import undetected_chromedriver as uc

def save_cookies():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    # undetected_chromedriver는 자체적으로 회피 옵션을 많이 포함하므로, 기존 옵션 일부는 제거해도 됩니다.
    
    print("봇 탐지 회피 기능이 강화된 브라우저를 시작합니다...")
    driver = uc.Chrome(options=options)

    driver.get("https://x.com/login")
    print("브라우저가 열렸습니다. 5분 안에 직접 로그인하세요.")
    print("이메일 인증, CAPTCHA 등이 뜨면 직접 처리해주세요.")

    time.sleep(300)  # 로그인 완료 대기 시간 5분

    cookies = driver.get_cookies()
    with open("twitter_cookies.pkl", "wb") as f:
        pickle.dump(cookies, f)

    print("\n[성공] twitter_cookies.pkl 저장 완료")
    driver.quit()

if __name__ == "__main__":
    save_cookies()
