# -*- coding: utf-8 -*-
import os
import asyncio
import time
import re
from datetime import datetime, timedelta
from collections import defaultdict

from scraper import WebScraper
from config import CATEGORIES

class TrendAnalyzer:
    """
    데이터를 분석하고 리포트를 생성하는 클래스.
    """
    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), 'results')
        os.makedirs(self.output_dir, exist_ok=True)

    def analyze_and_categorize(self, all_site_content):
        """
        수집된 모든 사이트의 콘텐츠를 종합하여 카테고리별로 분류합니다.
        """
        print("n--- 2단계: 카테고리 분석 ---")
        categorized_results = defaultdict(list)
        
        all_content = set()
        for site_data in all_site_content.values():
            all_content.update(site_data)
        
        print(f"[Info] 총 {len(all_content)}개의 고유 콘텐츠 분석 시작...")

        for item in all_content:
            # 너무 짧거나 단순한 숫자/특수문자로만 이루어진 콘텐츠는 분석에서 제외
            if len(item) < 3 or item.isdigit():
                continue

            matched = False
            for category, patterns in CATEGORIES.items():
                for pattern in patterns:
                    if pattern.lower() in item.lower():
                        categorized_results[category].append(item)
                        matched = True
                        break
                if matched:
                    break
            if not matched:
                categorized_results['기타'].append(item)
        
        print("[Success] 카테고리 분석 완료.")
        return categorized_results

    def generate_report(self, site_contents, analyzed_data):
        """
        분석된 데이터를 기반으로 최종 텍스트 리포트를 생성합니다.
        """
        print("n--- 3단계: 리포트 생성 ---")
        kst = datetime.utcnow() + timedelta(hours=9)
        filename = f"Trend_Report_{kst.strftime('%Y-%m-%d_%H%M%S')}.txt"
        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("="*80 + "n")
                f.write(f" Trend Master V3 - 최종 리포트n")
                f.write(f" 조사 시간: {kst.strftime('%Y-%m-%d %H:%M:%S')} KSTn")
                f.write("="*80 + "nn")

                f.write("1. 플랫폼별 주요 트렌드n")
                f.write("-"*80 + "n")
                for site, contents in site_contents.items():
                    f.write(f"n--- [ {site.upper()} ] ---n")
                    if contents:
                        for i, content in enumerate(contents[:20], 1): # 사이트별 20개로 제한
                            f.write(f"{i}. {content}n")
                    else:
                        f.write("수집된 데이터가 없습니다.n")
                f.write("n" * 2)

                f.write("2. 종합 트렌드 요약n")
                f.write("-"*80 + "n")
                
                # '기타' 카테고리를 제외하고, 항목이 많은 순으로 정렬
                sorted_categories = sorted(
                    [k for k in analyzed_data.keys() if k != '기타'], 
                    key=lambda k: len(analyzed_data[k]), 
                    reverse=True
                )

                for category in sorted_categories:
                    items = list(set(analyzed_data[category])) # 중복 제거
                    if items:
                        f.write(f"n# {category} ({len(items)}개)n")
                        for i, item in enumerate(items[:15], 1): # 카테고리별 15개로 제한
                            f.write(f"- {item.strip()}n")
            
            print(f"[Success] 리포트 생성 완료: /app/results/{filename}")

        except Exception as e:
            print(f"[Fatal Error] 리포트 저장 중 심각한 오류 발생: {e}")

async def main():
    start_time = time.time()
    kst_now = (datetime.utcnow() + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')
    print("="*60)
    print(f" Trend Master V3 (Final Version) 시작")
    print(f" 시작 시간: {kst_now} KST")
    print("="*60)

    analyzer = TrendAnalyzer()

    async with WebScraper() as scraper:
        site_contents = await scraper.get_content_from_sites()

    analyzed_data = analyzer.analyze_and_categorize(site_contents)
    analyzer.generate_report(site_contents, analyzed_data)

    end_time = time.time()
    print(f"n총 실행 시간: {end_time - start_time:.2f}초")
    print("="*60)

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
