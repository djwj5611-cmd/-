# scraper.py
import os
import time
import pickle
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ===== 1. 공통 드라이버 생성 (GitHub Actions 호환) =====
def create_stealth_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # 스텔스 옵션 추가
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # GitHub Actions 환경에서는 ChromeDriver 경로를 직접 지정할 필요 없이
    # setup-chrome 액션이 자동으로 처리해줍니다.
    try:
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("✅ 스텔스 드라이버 생성 성공")
        return driver
    except Exception as e:
        print(f"❌ 드라이버 생성 실패: {e}")
        return None

# ===== 2. 데이터 수집 함수들 =====

# NAVER (requests)
def collect_naver_trends():
    try:
        print("\n[NAVER] 실시간 키워드 수집 시작...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        res = requests.get("https://signal.bz/", headers=headers, timeout=10) # 메인 페이지 사용
        soup = BeautifulSoup(res.text, "html.parser")
        # 사이트 내 여러 랭킹 키워드를 모두 대상으로 하여 더 안정적으로 수집
        keywords = [el.get_text(strip=True) for el in soup.select('.rank-keyword .keyword')]
        unique_keywords = list(dict.fromkeys(keywords)) # 중복 제거
        print(f"✅ [성공] {len(unique_keywords)}개 수집 완료")
        return unique_keywords[:10]
    except Exception as e:
        print(f"❌ [실패] NAVER 수집 실패: {e}")
        return []

# Google Trends (selenium)
def collect_google_trends(driver):
    try:
        print("\n[GOOGLE] 인기 검색어 수집 시작...")
        driver.get("https://trends.google.com/trends/trendingsearches/daily?geo=KR")
        # 리스트 전체를 감싸는 컨테이너가 로드될 때까지 대기
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.feed-list-wrapper"))
        )
        elements = driver.find_elements(By.CSS_SELECTOR, "div.feed-item-header div.title a")
        keywords = [el.text.strip() for el in elements if el.text.strip()]
        print(f"✅ [성공] {len(keywords)}개 수집 완료")
        return keywords[:10]
    except Exception as e:
        print(f"❌ [실패] GOOGLE 수집 실패: {e}")
        driver.save_screenshot("google_error.png")
        return []

# DCInside (requests)
def collect_dcinside_trends():
    try:
        print("\n[DCINSIDE] 실시간 베스트 수집 시작...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = "https://gall.dcinside.com/board/lists/?id=hit"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        # 공지 제외하고 게시물만 선택
        titles = [el.text.strip() for el in soup.select("tr.ub-content.us-post .gall_tit a:not(.icon_notice)")]
        print(f"✅ [성공] {len(titles)}개 수집 완료")
        return titles[:10]
    except Exception as e:
        print(f"❌ [실패] DCINSIDE 수집 실패: {e}")
        return []

# Theqoo (requests)
def collect_theqoo_trends():
    try:
        print("\n[THEQOO] HOT 게시물 수집 시작...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = "https://theqoo.net/hot"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        # 클래스 이름에 의존하지 않고, 제목 셀 내부의 링크를 직접 선택
        titles = [el.text.strip() for el in soup.select('td.title a') if '[공지]' not in el.text]
        print(f"✅ [성공] {len(titles)}개 수집 완료")
        return titles[:20] # 더쿠는 HOT 게시물이 많으므로 20개 수집
    except Exception as e:
        print(f"❌ [실패] THEQOO 수집 실패: {e}")
        return []


# Twitter (쿠키 로그인 및 데이터 수집)
def twitter_cookie_login(driver):
    try:
        print("\n[TWITTER] 쿠키 로그인 시도...")
        driver.get("https://x.com/")
        cookie_file = "twitter_cookies.pkl"
        if not os.path.exists(cookie_file):
            print("❌ twitter_cookies.pkl 파일이 없습니다.")
            return False

        with open(cookie_file, "rb") as f:
            cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)

        driver.refresh()
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[@data-testid='AppTabBar_Home_Link']"))
        )
        print("✅ 트위터 쿠키 로그인 성공")
        return True
    except Exception as e:
        print(f"❌ 트위터 쿠키 로그인 실패: {e}")
        driver.save_screenshot("twitter_login_failed.png")
        return False

def collect_twitter_data(driver):
    try:
        print("[TWITTER] 트렌드 수집 시작...")
        driver.get("https://x.com/explore/tabs/trending")
        # 트렌드 데이터가 로드될 때까지 명시적으로 대기
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='trend']"))
        )
        trends = driver.find_elements(By.XPATH, "//div[@data-testid='trend']//span")
        # '#'이 포함된 키워드만 필터링하지 않고, 주요 텍스트를 가져옴
        keywords = [t.text for t in trends if t.text.strip() and not t.text.isdigit() and 'Trending' not in t.text and 'posts' not in t.text]
        # 중복 제거 및 순서 유지
        unique_keywords = list(dict.fromkeys(keywords))
        print(f"✅ [성공] {len(unique_keywords)}개 수집 완료")
        return unique_keywords[:10]
    except Exception as e:
        print(f"❌ [실패] TWITTER 수집 실패: {e}")
        return []

# ===== 3. 메인 실행 로직 =====
def main():
    # Selenium을 사용하는 수집 작업
    driver = create_stealth_driver()
    if driver:
        google_keywords = collect_google_trends(driver)
        
        twitter_keywords = []
        if twitter_cookie_login(driver):
            twitter_keywords = collect_twitter_data(driver)
        driver.quit()
    else:
        google_keywords, twitter_keywords = [], []

    # requests를 사용하는 수집 작업 (드라이버 필요 없음)
    naver_keywords = collect_naver_trends()
    dcinside_keywords = collect_dcinside_trends()
    theqoo_keywords = collect_theqoo_trends()

    # 리포트 생성
    os.makedirs("reports", exist_ok=True)
    report_path = f"reports/Trend_Report_{time.strftime('%Y-%m-%d_%H%M%S')}.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"=== Trend Report ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n\n")
        f.write("■ NAVER\n" + ("\n".join(f"- {k}" for k in naver_keywords) if naver_keywords else "데이터 수집 실패") + "\n\n")
        f.write("■ Google Trends\n" + ("\n".join(f"- {k}" for k in google_keywords) if google_keywords else "데이터 수집 실패") + "\n\n")
        f.write("■ DCInside\n" + ("\n".join(f"- {k}" for k in dcinside_keywords) if dcinside_keywords else "데이터 수집 실패") + "\n\n")
        f.write("■ Theqoo\n" + ("\n".join(f"- {k}" for k in theqoo_keywords) if theqoo_keywords else "데이터 수집 실패") + "\n\n")
        f.write("■ Twitter(X)\n" + ("\n".join(f"- {k}" for k in twitter_keywords) if twitter_keywords else "데이터 수집 실패 또는 쿠키 파일 없음") + "\n")
    
    print(f"\n📊 리포트 저장 완료: {report_path}")

if __name__ == "__main__":
    main()