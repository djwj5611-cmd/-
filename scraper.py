# scraper.py (Hybrid Final Version)
import os
import time
import json
from playwright.sync_api import sync_playwright
from pytrends.request import TrendReq
from gnews import GNews

# ===== 인간적인 행동 패턴 클래스 =====
class HumanLike:
    @staticmethod
    async def human_type(page, selector, text):
        await page.click(selector)
        for char in text:
            await page.keyboard.type(char)
            await page.wait_for_timeout(float(f"0.{str(time.time())[-3:]}") * 0.4 + 0.1)

    @staticmethod
    async def natural_scroll(page):
        for _ in range(3):
            await page.mouse.wheel(0, 1500)
            await page.wait_for_timeout(float(f"0.{str(time.time())[-3:]}") * 2 + 1)

# ===== 준(準) API 수집 함수들 =====
def collect_google_trends_api():
    try:
        print("\n[Google Trends API] 데이터 수집 시작...")
        pytrends = TrendReq(hl='ko-KR', tz=540)
        trending = pytrends.trending_searches(pn='south_korea')
        keywords = trending[0].tolist()
        print(f"✅ [성공] {len(keywords)}개 수집 완료")
        return keywords
    except Exception as e:
        print(f"❌ [실패] Google Trends API 수집 실패: {e}")
        return []

def collect_news_api(keyword):
    try:
        print(f"\n[News API] '{keyword}' 관련 뉴스 수집 시작...")
        gnews = GNews(language='ko', country='KR', period='1d')
        articles = gnews.get_news(keyword)
        results = [{"title": a['title'], "url": a['url']} for a in articles[:5]]
        print(f"✅ [성공] {len(results)}개 뉴스 수집 완료")
        return results
    except Exception as e:
        print(f"❌ [실패] News API 수집 실패: {e}")
        return []

# ===== Playwright 스크래핑 함수들 =====
def collect_twitter_data(page, keyword):
    # ... (이전의 상세 검색 로직과 유사하게 구현) ...
    return [{"title": f"'{keyword}'에 대한 트윗 1"}, {"title": f"'{keyword}'에 대한 트윗 2"}]

# ===== 메인 실행 로직 =====
def main():
    # 1. 준 API 방식으로 키워드 및 뉴스 수집
    google_trends = collect_google_trends_api()
    main_keyword = google_trends[0] if google_trends else "대한민국"
    news_results = collect_news_api(main_keyword)

    # 2. Playwright로 로그인 기반 사이트 수집
    twitter_results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        auth_file = "auth/twitter_auth.json"
        if os.path.exists(auth_file):
            context = browser.new_context(storage_state=auth_file)
            page = context.new_page()
            twitter_results = collect_twitter_data(page, main_keyword)
            context.close()
        else:
            print("❌ twitter_auth.json 파일이 없어 트위터 수집을 건너뜁니다.")
        browser.close()

    # 3. 최종 리포트 생성
    os.makedirs("reports", exist_ok=True)
    report_path = f"reports/Hybrid_Trend_Report_{{time.strftime('%Y-%m-%d')}}.json"
    final_report = {
        "update_time": datetime.now().isoformat(),
        "google_trends": google_trends,
        "related_news": {main_keyword: news_results},
        "twitter_buzz": {main_keyword: twitter_results}
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 하이브리드 리포트 저장 완료: {report_path}")

if __name__ == "__main__":
    main()
