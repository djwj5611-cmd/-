# -*- coding: utf-8 -*-
import asyncio
import random
import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from config import USER_AGENTS, SITES, MIN_WAIT, MAX_WAIT

class WebScraper:
    """
    Playwright를 사용하여 웹사이트에서 데이터를 비동기적으로 스크래핑하는 클래스.
    네트워크 안정화 및 동적 콘텐츠 로딩을 기다리는 고도화된 로직을 사용합니다.
    """
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
        """인간적인 딜레이를 추가합니다."""
        delay = seconds if seconds is not None else random.uniform(MIN_WAIT, MAX_WAIT)
        await asyncio.sleep(delay)

    async def get_content_from_sites(self):
        """
        config.py의 SITES를 순회하며, 각 사이트의 구조에 맞춰 핵심 콘텐츠를 추출합니다.
        """
        site_contents = {}
        print("n--- 1단계: 전체 사이트 데이터 수집 ---")

        for site_key, site_info in SITES.items():
            context = None
            page = None
            try:
                print(f"[{site_key}] 데이터 수집 중...")
                context = await self.browser.new_context(user_agent=random.choice(USER_AGENTS))
                page = await context.new_page()
                
                # 네트워크가 안정될 때까지 기다려 동적 콘텐츠 로딩 보장
                await page.goto(site_info['url'], timeout=60000, wait_until='networkidle')
                
                # 스크롤을 통해 lazy-loading 콘텐츠를 불러옴
                await page.evaluate('window.scrollBy(0, window.innerHeight)')
                await self._human_like_wait(1) # 스크롤 후 로딩 대기

                # 지정된 selector가 나타날 때까지 대기
                await page.wait_for_selector(site_info['selector'], timeout=20000)
                
                elements = await page.locator(site_info['selector']).all_text_contents()
                
                # 텍스트 정제: 불필요한 공백, 줄바꿈, 특정 패턴 제거
                content_list = []
                for text in elements:
                    clean_text = text.strip()
                    # FMKorea의 추천수, TheQoo의 카테고리 등 불필요한 부분 제거
                    clean_text = re.sub(r's*\[d+\]s*$', '', clean_text) # 끝에 붙는 [숫자] 제거
                    clean_text = re.sub(r'^(ㅇㅎ|ㅎㅂ|ㅅㅍ)s*s*', '', clean_text) # ㅇㅎ) 등 접두사 제거
                    if clean_text:
                        content_list.append(clean_text)

                site_contents[site_key] = content_list
                print(f"[{site_key}] 데이터 {len(content_list)}개 항목 수집 완료.")

            except PlaywrightTimeoutError:
                print(f"[Error][{site_key}] 페이지 로딩 또는 selector 대기 시간 초과.")
                site_contents[site_key] = []
            except Exception as e:
                print(f"[Error][{site_key}] 처리 중 오류: {e}")
                site_contents[site_key] = []
            finally:
                if page:
                    await page.close()
                if context:
                    await context.close()
        
        print(f"n[Success] 총 {len(SITES)}개 사이트에서 데이터 수집 시도 완료.")
        return site_contents
