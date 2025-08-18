# scraper.py
import os
import time
import pickle
import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

# ===== 1. 공통 드라이버 생성 (GitHub Actions 호환) =====
def create_stealth_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    try:
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("✅ 스텔스 드라이버 생성 성공")
        return driver
    except Exception as e:
        print(f"❌ 드라이버 생성 실패: {e}")
        return None

# ===== 2. 데이터 수집 함수들 (개선 버전) =====
def collect_naver_trends(driver):
    try:
        print("\n[NAVER] 실시간 키워드 수집 시작...")
        driver.get("https://signal.bz/")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.rank-keyword"))
        )
        elements = driver.find_elements(By.CSS_SELECTOR, 'div.rank-keyword span.keyword')
        keywords = [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]
        unique_keywords = list(dict.fromkeys(keywords))
        print(f"✅ [성공] {len(unique_keywords)}개 수집 완료")
        return unique_keywords[:10]
    except Exception as e:
        print(f"❌ [실패] NAVER 수집 실패: {e}")
        driver.save_screenshot("naver_error.png")
        return []

def collect_google_trends(driver):
    try:
        print("\n[GOOGLE] 인기 검색어 수집 시작...")
        driver.get("https://trends.google.com/trends/trendingsearches/daily?geo=KR")
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.feed-item-header div.title a"))
        )
        elements = driver.find_elements(By.CSS_SELECTOR, "div.feed-item-header div.title a")
        keywords = [el.text.strip() for el in elements if el.text.strip()]
        print(f"✅ [성공] {len(keywords)}개 수집 완료")
        return keywords[:10]
    except Exception as e:
        print(f"❌ [실패] GOOGLE 수집 실패: {e}")
        driver.save_screenshot("google_error.png")
        return []

def collect_dcinside_trends():
    try:
        print("\n[DCINSIDE] 실시간 베스트 수집 시작...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = "https://gall.dcinside.com/board/lists/?id=hit"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        titles = []
        for el in soup.select("tr.ub-content.us-post .gall_tit a:not(.icon_notice)"):
            title = el.text.strip()
            cleaned_title = re.sub(r'\s*\[\d+\]$', '', title)
            titles.append(cleaned_title)
        print(f"✅ [성공] {len(titles)}개 수집 완료")
        return titles[:10]
    except Exception as e:
        print(f"❌ [실패] DCINSIDE 수집 실패: {e}")
        return []

def collect_theqoo_trends():
    try:
        print("\n[THEQOO] HOT 게시물 수집 시작...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = "https://theqoo.net/hot"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        titles = []
        for row in soup.select("table.theqoo_hot_table tr:not(.notice)"):
            title_element = row.select_one('td.title a')
            if title_element:
                titles.append(title_element.text.strip())
        print(f"✅ [성공] {len(titles)}개 수집 완료")
        return titles[:20]
    except Exception as e:
        print(f"❌ [실패] THEQOO 수집 실패: {e}")
        return []

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
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//a[@data-testid='AppTabBar_Home_Link']")))
        print("✅ 트위터 쿠키 로그인 성공")
        return True
    except Exception as e:
        print(f"❌ 트위터 쿠키 로그인 실패: {e}")
        driver.save_screenshot("twitter_login_failed.png")
        return False

def collect_twitter_data(driver):
    print("\n[TWITTER] 채용 공고 상세 검색 시작...")
    base_keywords = ["스텝", "스태프", "직원", "팀원", "팀", "매니저"]
    action_keywords = ["공고", "구인", "채용", "모집"]
    search_keywords = [f"{base} {action}" for base in base_keywords for action in action_keywords]
    
    all_results = []
    processed_links = set()

    for keyword in search_keywords:
        try:
            print(f"  -> '{keyword}' 검색 중...")
            since_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            search_url = f"https://x.com/search?q={keyword}%20since%3A{since_date}&src=typed_query&f=live"
            driver.get(search_url)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
            )
            time.sleep(2)

            for _ in range(5):
                tweets = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
                for tweet in tweets:
                    try:
                        link_element = tweet.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]')
                        tweet_link = link_element.get_attribute('href')

                        if tweet_link in processed_links:
                            continue
                        
                        text = tweet.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]').text
                        post_time = tweet.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
                        user_info = tweet.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]').text.split('\n')
                        username = user_info[0] if user_info else "Unknown"

                        all_results.append({
                            'keyword': keyword,
                            'username': username,
                            'time': post_time,
                            'text': text,
                            'link': tweet_link
                        })
                        processed_links.add(tweet_link)
                    except Exception:
                        continue
                
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
        except Exception as e:
            print(f"    ❌ '{keyword}' 검색 실패: {e}")
            continue
    
    print(f"✅ [성공] 총 {len(all_results)}개 트윗 수집 완료")
    return sorted(all_results, key=lambda x: x['time'], reverse=True)

# ===== 3. 메인 실행 로직 =====
def main():
    driver = create_stealth_driver()
    if driver:
        naver_keywords = collect_naver_trends(driver)
        google_keywords = collect_google_trends(driver)
        twitter_results = []
        if twitter_cookie_login(driver):
            twitter_results = collect_twitter_data(driver)
        driver.quit()
    else:
        naver_keywords, google_keywords, twitter_results = [], [], []

    dcinside_keywords = collect_dcinside_trends()
    theqoo_keywords = collect_theqoo_trends()

    os.makedirs("reports", exist_ok=True)
    report_path = f"reports/Trend_Report_{{time.strftime('%Y-%m-%d_%H%M%S')}}.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"=== Trend Report ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n\n")
        f.write("■ NAVER\n" + ("\n".join(f"- {k}" for k in naver_keywords) if naver_keywords else "데이터 수집 실패") + "\n\n")
        f.write("■ Google Trends\n" + ("\n".join(f"- {k}" for k in google_keywords) if google_keywords else "데이터 수집 실패") + "\n\n")
        f.write("■ DCInside\n" + ("\n".join(f"- {k}" for k in dcinside_keywords) if dcinside_keywords else "데이터 수집 실패") + "\n\n")
        f.write("■ Theqoo\n" + ("\n".join(f"- {k}" for k in theqoo_keywords) if theqoo_keywords else "데이터 수집 실패") + "\n\n")
        
        f.write("---\n\n")
        f.write(f"=== 트위터 스태프 모집 검색 결과 ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n")
        f.write(f"총 {len(twitter_results)}개 발견\n\n")
        
        if twitter_results:
            for i, result in enumerate(twitter_results, 1):
                f.write(f"[{i}] 검색 키워드: {result['keyword']}\n")
                f.write(f"작성자: {result['username']}\n")
                f.write(f"시간: {result['time']}\n")
                f.write(f"내용: {result['text']}\n")
                f.write(f"링크: {result['link']}\n")
                f.write("---" * 70 + "\n\n")
        else:
            f.write("데이터 수집에 실패했거나 새로운 공고가 없습니다.\n")

    print(f"\n📊 리포트 저장 완료: {report_path}")

if __name__ == "__main__":
    main()
