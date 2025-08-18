# save_cookies.py
import time
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

def save_cookies():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Selenium Stealth 적용
    stealth(driver,
            languages=["ko-KR", "ko"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    driver.get("https://x.com/login")
    print("브라우저가 열렸습니다. 5분 안에 직접 로그인하세요.")
    print("이메일 인증, CAPTCHA 등이 뜨면 직접 처리해주세요.")

    time.sleep(300)  # 로그인 완료 대기 시간 5분으로 변경

    cookies = driver.get_cookies()
    with open("twitter_cookies.pkl", "wb") as f:
        pickle.dump(cookies, f)

    print("\n[성공] twitter_cookies.pkl 저장 완료")
    driver.quit()

if __name__ == "__main__":
    save_cookies()
