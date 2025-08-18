# config.py

# 1. 리서치할 카테고리 정의
CATEGORIES = {
    "정치": ["정치", "대통령", "국회"],
    "경제": ["경제", "금리", "주식"],
    "엔터사": ["엔터테인먼트", "아이돌", "하이브", "SM"],
    "게임": ["게임", "LoL", "T1", "젠지"],
    "애니메이션": ["애니메이션", "최애의 아이"],
    "웹툰": ["웹툰", "네이버웹툰"],
    "굿즈": ["굿즈", "피규어", "팝업스토어"],
    "최신 밈": ["밈", "최신 밈", "유행어"]
}

# 2. 키워드 발굴을 위한 타겟 사이트
KEYWORD_SOURCES = {
    "google_news": "https://news.google.com/home?hl=ko&gl=KR&ceid=KR:ko"
}

# 3. 심층 분석을 위한 타겟 사이트
TARGET_SITES = {
    "twitter": "https://x.com",
    "dcinside": "https://www.dcinside.com",
    "pemco": "https://www.fmkorea.com",
    "google_news": "https://news.google.com"
}

# 4. 시간 범위 설정 (KST 기준)
TIME_RANGE_HOURS = 24

# 5. 결과 및 인증 파일 경로
RESULTS_DIR = "results"
AUTH_FILE = "auth/auth_state.json"
SCREENSHOTS_DIR = "screenshots"
