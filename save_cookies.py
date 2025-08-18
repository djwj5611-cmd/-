# save_cookies.py
import time
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def save_cookies():
  options = webdriver.ChromeOptions()
  # headless 모드 비활성화 → 직접 로그인 화면 확인 가능
  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

  driver.get("https://x.com/login")
  print("브라우저가 열렸습니다. 60초 안에 직접 로그인하세요.")
  print("이메일 인증, CAPTCHA 등이 뜨면 직접 처리해주세요.")

  time.sleep(60)  # 로그인 완료 대기

  cookies = driver.get_cookies()
  with open("twitter_cookies.pkl", "wb") as f:
      pickle.dump(cookies, f)

  print("\n[성공] twitter_cookies.pkl 저장 완료")
  driver.quit()

if __name__ == "__main__":
  save_cookies()
