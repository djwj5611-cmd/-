
# keyword_manager.py
import sys
from pytrends.request import TrendReq

def get_google_trends():
    try:
        pytrends = TrendReq(hl='ko-KR', tz=540)
        trends = pytrends.trending_searches(pn='south_korea')
        print("Successfully fetched Google Trends.")
        return trends[0].tolist()[:5] # 상위 5개 키워드만 반환
    except Exception as e:
        print(f"Error fetching Google Trends: {e}", file=sys.stderr)
        return []

def main():
    # 여기에 네이버, 다음 등 다른 소스에서 키워드를 가져오는 로직 추가 가능
    google_keywords = get_google_trends()
    
    # 기본 키워드와 조합
    base_keywords = ["채용", "구인", "스태프 모집", "팀원 모집"]
    final_keywords = list(set(google_keywords + base_keywords))
    
    print(f"Final keywords: {final_keywords}")

    with open("keywords.json", "w", encoding="utf-8") as f:
        import json
        json.dump(final_keywords, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
