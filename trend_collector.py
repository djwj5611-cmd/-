# 파일명: trend_collector.py

import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from collections import defaultdict
import os
import random
import traceback

class UltimateTrendCollector:
    """
    GitHub Actions에서 안정적으로 실행되도록 최종 수정된 버전입니다.
    """
    def __init__(self, stealth_mode=True):
        self.stealth_mode = stealth_mode
        # 중요: 절대 경로 대신, 스크립트 실행 위치에 'reports' 폴더를 만듭니다.
        self.output_dir = os.path.join(os.getcwd(), 'reports')
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        ]
        self.headers = {'User-Agent': random.choice(self.user_agents)}
        self.driver = None
        self.wait = None
        self.platform_data = defaultdict(list)

    def create_stealth_driver(self):
        print("\n[드라이버] 스텔스 모드로 드라이버를 시작합니다...")
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920x1080')
        options.add_argument(f'user-agent={random.choice(self.user_agents)}')

        if self.stealth_mode:
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            if self.stealth_mode:
                stealth(self.driver, languages=["ko-KR", "ko"], vendor="Google Inc.", platform="Linux", webgl_vendor="Intel Inc.", fix_hairline=True)
            self.wait = WebDriverWait(self.driver, 15)
            print("   [성공] 스텔스 드라이버 시작 완료")
        except Exception as e:
            print(f"   [실패] 드라이버 시작 중 오류 발생: {e}")
            self.driver = None

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("\n... 웹 드라이버를 안전하게 종료했습니다 ...")

    def collect_naver_trends(self):
        print("\n[NAVER] 실시간 키워드 수집 시작...")
        try:
            response = requests.get('https://www.signal.bz/', headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            keywords = [elem.get_text(strip=True) for elem in soup.select('div.rank-keyword span.keyword') if elem.get_text(strip=True)]
            self.platform_data['NAVER'] = list(dict.fromkeys(keywords))[:10]
            print(f"   [성공] {len(self.platform_data['NAVER'])}개 수집 완료")
        except Exception as e: print(f"   [실패] NAVER 수집 실패: {e}")

    def collect_google_trends(self):
        if not self.driver: return
        print("\n[GOOGLE] 인기 검색어 수집 시작...")
        try:
            self.driver.get('https://trends.google.com/trends/trendingsearches/daily?geo=KR')
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.feed-item-header")))
            headlines = [elem.text.strip() for elem in self.driver.find_elements(By.CSS_SELECTOR, 'div.feed-item-header > a > span') if elem.text.strip()]
            self.platform_data['GOOGLE'] = headlines[:15]
            print(f"   [성공] {len(self.platform_data['GOOGLE'])}개 수집 완료")
        except Exception as e: print(f"   [실패] GOOGLE 수집 실패: {e}")
    
    def collect_dcinside_trends(self):
        if not self.driver: return
        print("\n[DCINSIDE] 실시간 베스트 게시물 수집 시작...")
        try:
            self.driver.get('https://www.dcinside.com/')
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.box_best_main')))
            titles = [elem.text.strip() for elem in self.driver.find_elements(By.CSS_SELECTOR, 'div.box_best_main ul li a') if elem.text.strip()]
            self.platform_data['DCINSIDE'] = titles[:20]
            print(f"   [성공] {len(self.platform_data['DCINSIDE'])}개 수집 완료")
        except Exception as e: print(f"   [실패] DCINSIDE 수집 실패: {e}")

    def collect_theqoo_trends(self):
        if not self.driver: return
        print("\n[THEQOO] HOT 게시물 수집 시작...")
        try:
            self.driver.get('https://theqoo.net/hot')
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.theqoo_hot_board_list')))
            titles = [re.sub(r'\s*\[\d+\]$', '', elem.text).strip() for elem in self.driver.find_elements(By.CSS_SELECTOR, 'table.theqoo_hot_board_list td.title a') if '[공지]' not in elem.text and len(elem.text.strip()) > 5]
            self.platform_data['THEQOO'] = titles[:20]
            print(f"   [성공] {len(self.platform_data['THEQOO'])}개 수집 완료")
        except Exception as e: print(f"   [실패] THEQOO 수집 실패: {e}")

    def generate_report(self):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        filename = f"Trend_Report_{timestamp}.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        report_lines = [f"=== Trend Report ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - via GitHub Actions) ==="]
        platform_order = ['NAVER', 'GOOGLE', 'DCINSIDE', 'THEQOO']
        for platform in platform_order:
            if self.platform_data.get(platform):
                report_lines.append(f"\n\n--- [ {platform} ] ---")
                for i, item in enumerate(self.platform_data[platform], 1):
                    report_lines.append(f"{i}. {item}")
        
        with open(filepath, 'w', encoding='utf-8') as f: f.write('\n'.join(report_lines))
        print(f"\n[성공] 최종 리포트 생성 완료! 경로: {filepath}")

    def run(self):
        try:
            self.create_stealth_driver()
            self.collect_naver_trends()
            if self.driver:
                self.collect_google_trends()
                self.collect_dcinside_trends()
                self.collect_theqoo_trends()
            self.generate_report()
        finally:
            self.close_driver()

if __name__ == "__main__":
    collector = UltimateTrendCollector()
    collector.run()
