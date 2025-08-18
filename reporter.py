# reporter.py
import os
from datetime import datetime
from config import RESULTS_DIR

def save_reports(keywords, results):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    # 1. 사용된 키워드 리포트
    keywords_path = os.path.join(RESULTS_DIR, f"{today}_사용한_키워드.txt")
    with open(keywords_path, 'w', encoding='utf-8') as f:
        f.write(f"=== {today} 트렌드 리서치 V3 - 사용된 키워드 ===\n\n")
        for category, kws in keywords.items():
            f.write(f"[{category}]\n")
            f.write(", ".join(kws) + "\n\n")
    print(f"[성공] 키워드 리포트 저장: {keywords_path}")

    # 2. 카테고리별 분석 결과 리포트
    results_path = os.path.join(RESULTS_DIR, f"{today}_카테고리별_분석_결과.txt")
    with open(results_path, 'w', encoding='utf-8') as f:
        f.write(f"=== {today} 트렌드 리서치 V3 - 카테고리별 분석 결과 ===\n\n")
        
        # 카테고리별로 결과 그룹화
        grouped_results = {cat: [] for cat in keywords}
        for res in results:
            if res['category'] in grouped_results:
                grouped_results[res['category']].append(res)

        for category, items in grouped_results.items():
            f.write(f"--- {category} ---\n\n")
            if not items:
                f.write("수집된 데이터가 없습니다.\n\n")
                continue
            
            for item in items:
                f.write(f"키워드: {item['keyword']}\n")
                f.write(f"사이트: {item['site']}\n")
                f.write(f"제목/내용: {item['title'][:100]}...\n")
                f.write(f"링크: {item['link']}\n")
                f.write("-" * 30 + "\n")
            f.write("\n")
    print(f"[성공] 분석 결과 리포트 저장: {results_path}")
