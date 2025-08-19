# keyword_manager.py

import json
import os
from pytrends.request import TrendReq

def get_google_trends_keywords():
    """Google Trends에서 일일 인기 검색어 20개를 가져옵니다."""
    print("[PY] Google Trends 인기 검색어 수집 시작...")
    try:
        pytrends = TrendReq(hl='ko-KR', tz=540)
        df = pytrends.trending_searches(pn='south_korea')
        keywords = df[0].tolist()
        if not keywords:
            print("⚠️ [PY] Google Trends에서 키워드를 가져왔지만, 리스트가 비어있습니다.")
            return []
        print(f"✅ [PY] 인기 검색어 {len(keywords)}개 수집 완료")
        return keywords[:10] # 수집 키워드 수를 10개로 줄여 너무 많은 크롤링 방지
    except Exception as e:
        print(f"❌ [PY] Google Trends 수집 실패: {e}")
        return []

def main():
    # 백업용 기본 키워드 리스트 정의
    base_keywords = ["스태프 모집", "팀원 구인", "개발자 채용", "디자이너 구인", "마케터 채용"]
    print(f"[PY] 기본 키워드: {base_keywords}")

    # Google Trends 키워드 가져오기
    google_keywords = get_google_trends_keywords()

    # 두 리스트를 합치고 중복을 제거하여 최종 키워드 리스트 생성
    # Google Trends 수집에 실패하면 google_keywords는 빈 리스트가 되어 base_keywords만 남게 됨
    final_keywords = list(set(google_keywords + base_keywords))
    
    os.makedirs('data', exist_ok=True)
    
    with open("data/keywords_for_js.json", "w", encoding="utf-8") as f:
        json.dump(final_keywords, f, ensure_ascii=False)

    if not final_keywords:
        print("⚠️ [PY] 최종 키워드가 없어 Node.js 크롤링을 진행하지 않습니다.")
    else:
        print("\n✅ [PY] `keywords_for_js.json` 생성을 완료했습니다.")
        print(f"전달할 최종 키워드: {final_keywords}")

if __name__ == "__main__":
    main()
