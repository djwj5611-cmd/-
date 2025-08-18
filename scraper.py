# scraper.py (Final Stable Version)
import os
import time
import requests
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

# ===== 데이터 수집 함수들 =====
def collect_naver_trends(page):
    try:
        print("\n[NAVER] 수집 시작...")
        page.goto("https://signal.bz/", wait_until='domcontentloaded', timeout=30000)
        page.wait_for_selector('div.rank-keyword span.keyword', timeout=15000)
        elements = page.locator('div.rank-keyword span.keyword').all()
        keywords = list(dict.fromkeys([el.inner_text() for el in elements if el.inner_text()]))
        print(f"✅ [성공] {len(keywords)}개 수집")
        return keywords[:10]
    except Exception as e:
        print(f"❌ [실패] NAVER: {e}")
        page.screenshot(path="screenshots/naver_error.png")
        return []

def collect_google_trends(page):
    try:
        print("\n[GOOGLE] 수집 시작...")
        page.goto("https://trends.google.com/trends/trendingsearches/daily?geo=KR", wait_until='domcontentloaded', timeout=30000)
        page.wait_for_selector("div.feed-item-header div.title a", timeout=15000)
        elements = page.locator("div.feed-item-header div.title a").all()
        keywords = [el.inner_text().strip() for el in elements if el.inner_text().strip()]
        print(f"✅ [성공] {len(keywords)}개 수집")
        return keywords[:10]
    except Exception as e:
        print(f"❌ [실패] GOOGLE: {e}")
        page.screenshot(path="screenshots/google_error.png")
        return []

def collect_dcinside_trends():
    try:
        print("\n[DCINSIDE] 수집 시작...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}
        res = requests.get("https://gall.dcinside.com/board/lists/?id=hit", headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        titles = [re.sub(r'\s*\[\d+\]$', '', el.text.strip()) for el in soup.select("tr.ub-content.us-post .gall_tit a:not(.icon_notice)")]
        print(f"✅ [성공] {len(titles)}개 수집")
        return titles[:10]
    except Exception as e:
        print(f"❌ [실패] DCINSIDE: {e}")
        return []

def collect_theqoo_trends():
    try:
        print("\n[THEQOO] 수집 시작...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}
        res = requests.get("https://theqoo.net/hot", headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        titles = [el.text.strip() for row in soup.select("table.theqoo_hot_table tr:not(.notice)") if (el := row.select_one('td.title a'))]
        print(f"✅ [성공] {len(titles)}개 수집")
        return titles[:20]
    except Exception as e:
        print(f"❌ [실패] THEQOO: {e}")
        return []

def collect_twitter_data(page):
    print("\n[TWITTER] 채용 공고 검색 시작...")
    base_keywords = ["스텝", "스태프", "직원", "팀원", "팀", "매니저"]
    action_keywords = ["공고", "구인", "채용", "모집"]
    search_keywords = [f"{base} {action}" for base in base_keywords for action in action_keywords]
    all_results = []
    processed_links = set()

    for keyword in search_keywords:
        try:
            print(f"  -> '{keyword}' 검색...")
            since_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            search_url = f"https://x.com/search?q={keyword}%20since%3A{since_date}&src=typed_query&f=live"
            page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
            
            for _ in range(3):
                page.mouse.wheel(0, 1500)
                time.sleep(1.5)

            tweets = page.locator('article[data-testid="tweet"]').all()
            for tweet in tweets:
                try:
                    link_element = tweet.locator('a[href*="/status/"]').first
                    tweet_link = link_element.get_attribute('href')
                    if tweet_link in processed_links: continue
                    
                    text = tweet.locator('[data-testid="tweetText"]').inner_text()
                    post_time = tweet.locator('time').get_attribute('datetime')
                    username = tweet.locator('[data-testid="User-Name"]').inner_text().split('\n')[0]

                    all_results.append({'keyword': keyword, 'username': username, 'time': post_time, 'text': text, 'link': f"https://x.com{tweet_link}"})
                    processed_links.add(tweet_link)
                except Exception: continue
        except Exception as e:
            print(f"    ❌ '{keyword}' 검색 실패: {e}")
            continue
    
    print(f"✅ [성공] 총 {len(all_results)}개 트윗 수집")
    return sorted(all_results, key=lambda x: x['time'], reverse=True)

# ===== 메인 실행 로직 =====
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--use-gl=egl'])
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        
        # Playwright 기반 수집
        page = browser.new_page(user_agent=user_agent)
        naver_keywords = collect_naver_trends(page)
        google_keywords = collect_google_trends(page)
        page.close()

        # 트위터 수집
        twitter_results = []
        auth_file = "auth/auth_state.json"
        if os.path.exists(auth_file):
            try:
                context = browser.new_context(storage_state=auth_file, user_agent=user_agent)
                page = context.new_page()
                twitter_results = collect_twitter_data(page)
                context.close()
            except Exception as e:
                print(f"❌ 트위터 컨텍스트 처리 중 오류: {e}")
        else:
            print("❌ auth.json 파일이 없어 트위터 수집을 건너뜁니다.")
        
        browser.close()

    # requests 기반 수집
    dcinside_keywords = collect_dcinside_trends()
    theqoo_keywords = collect_theqoo_trends()

    # 리포트 생성
    os.makedirs("reports", exist_ok=True)
    report_path = f"reports/Trend_Report_{{time.strftime('%Y-%m-%d_%H%M%S')}}.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"=== Trend Report ({time.strftime('%Y-%m-%d %H%M%S')}) ===\n\n")
        f.write("■ NAVER\n" + ("\n".join(f"- {k}" for k in naver_keywords) if naver_keywords else "데이터 수집 실패") + "\n\n")
        f.write("■ Google Trends\n" + ("\n".join(f"- {k}" for k in google_keywords) if google_keywords else "데이터 수집 실패") + "\n\n")
        f.write("■ DCInside\n" + ("\n".join(f"- {k}" for k in dcinside_keywords) if dcinside_keywords else "데이터 수집 실패") + "\n\n")
        f.write("■ Theqoo\n" + ("\n".join(f"- {k}" for k in theqoo_keywords) if theqoo_keywords else "데이터 수집 실패") + "\n\n")
        f.write("---\n\n")
        f.write(f"=== 트위터 스태프 모집 검색 결과 ({time.strftime('%Y-%m-%d %H%M%S')}) ===\n")
        f.write(f"총 {len(twitter_results)}개 발견\n\n")
        if twitter_results:
            for i, result in enumerate(twitter_results, 1):
                f.write(f"[{i}] 검색 키워드: {result['keyword']}\n"
                        f"작성자: {result['username']}\n"
                        f"시간: {result['time']}\n"
                        f"내용: {result['text']}\n"
                        f"링크: {result['link']}\n"
                        f"{'-' * 70}\n\n")
        else:
            f.write("데이터 수집에 실패했거나 새로운 공고가 없습니다.\n")
    print(f"\n📊 리포트 저장 완료: {report_path}")

if __name__ == "__main__":
    main()