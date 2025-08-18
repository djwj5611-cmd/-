# -*- coding: utf-8 -*-
import asyncio
import random
import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import stealth_async
from pytrends.request import TrendReq
from config import USER_AGENTS, SITES, MIN_WAIT, MAX_WAIT, PROXIES

class WebScraper:
    def __init__(self):
        self.browser = None
        self.playwright = None

    async def __aenter__(self):
        print("[Scraper] 초기화 시작...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        print("[Scraper] 초기화 완료.")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("n[Scraper] 리소스 정리 완료.")

    async def _human_like_wait(self, seconds=None):
        delay = seconds if seconds is not None else random.uniform(MIN_WAIT, MAX_WAIT)
        await asyncio.sleep(delay)

    async def _get_google_trends_from_api(self):
        """pytrends 라이브러리를 사용하여 Google Trends 데이터를 가져옵니다."""
        try:
            pytrends = TrendReq(hl='ko-KR', tz=540)
            trending_searches_df = pytrends.trending_searches(pn='south_korea')
            return trending_searches_df[0].tolist()
        except Exception as e:
            print(f"[Error][google_trends_api] 처리 중 오류: {e}")
            return []

    async def _get_content_from_playwright(self, site_key, site_info):
        """Playwright를 사용하여 웹사이트에서 콘텐츠를 스크래핑합니다."""
        context = None
        page = None
        try:
            proxy_server = random.choice(PROXIES) if PROXIES else None
            context_options = {
                'user_agent': random.choice(USER_AGENTS),
                'proxy': {'server': proxy_server} if proxy_server else None
            }
            context = await self.browser.new_context(**context_options)
            page = await context.new_page()
            await stealth_async(page)

            await page.goto(site_info['url'], timeout=60000, wait_until='networkidle')
            await page.evaluate('window.scrollBy(0, window.innerHeight)')
            await self._human_like_wait(1)
            await page.wait_for_selector(site_info['selector'], timeout=20000)
            
            elements = await page.locator(site_info['selector']).all_text_contents()
            
            content_list = []
            for text in elements:
                clean_text = text.strip()
                clean_text = re.sub(r's*\[d+\]s*$', '', clean_text)
                clean_text = re.sub(r'^(ㅇㅎ|ㅎㅂ|ㅅㅍ)s*s*', '', clean_text)
                if clean_text:
                    content_list.append(clean_text)
            return content_list
        finally:
            if page: await page.close()
            if context: await context.close()

    async def get_content_from_sites(self):
        """config.py의 SITES를 순회하며, 타입에 따라 API 또는 Playwright로 데이터를 수집합니다."""
        site_contents = {}
        print("n--- 1단계: 전체 사이트 데이터 수집 ---")

        for site_key, site_info in SITES.items():
            content_list = []
            try:
                print(f"[{site_key}] 데이터 수집 중...")
                if site_info.get('type') == 'api':
                    content_list = await self._get_google_trends_from_api()
                else: # 'scrape' 또는 타입 미지정
                    content_list = await self._get_content_from_playwright(site_key, site_info)
                
                site_contents[site_key] = content_list
                print(f"[{site_key}] 데이터 {len(content_list)}개 항목 수집 완료.")
            except Exception as e:
                print(f"[Error][{site_key}] 처리 중 오류: {e}")
                site_contents[site_key] = []
        
        print(f"n[Success] 총 {len(SITES)}개 사이트에서 데이터 수집 시도 완료.")
        return site_contents
