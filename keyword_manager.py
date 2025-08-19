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
        if not keywords: # 키워드 리스트가 비어있는 경우도 처리
            print("⚠️ [PY] Google Trends에서 키워드를 가져왔지만, 리스트가 비어있습니다.")
            return []
        print(f"✅ [PY] 인기 검색어 {len(keywords)}개 수집 완료")
        return keywords[:20]
    except Exception as e:
        # 404 오류 등을 포함한 모든 예외 처리
        print(f"❌ [PY] Google Trends 수집 실패: {e}")
        return []  # 실패 시 안전하게 빈 리스트 반환

def main():
    raw_keywords = get_google_trends_keywords()
    
    # 디렉토리 생성은 항상 실행
    os.makedirs('data', exist_ok=True)
    
    # 키워드가 비어있더라도 파일은 생성하여 Node.js 스크립트가 오류 없이 읽도록 함
    with open("data/keywords_for_js.json", "w", encoding="utf-8") as f:
        json.dump(raw_keywords, f, ensure_ascii=False)

    if not raw_keywords:
        print("⚠️ [PY] 유효한 키워드가 없어 Node.js 크롤링을 진행하지 않습니다.")
    else:
        print("\n✅ [PY] `keywords_for_js.json` 생성을 완료했습니다.")
        print(f"전달할 키워드: {raw_keywords}")

if __name__ == "__main__":
    main()