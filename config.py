# -*- coding: utf-8 -*-

# 분석할 카테고리와 관련 패턴 정의
CATEGORIES = {
    '정치/사회': ['대통령', '김건희', '국회', '정당', '선거', '정책', '장관', '의원', '정부', '민주당', '국민의힘', '외교', '안보', '특검', '압수수색', '경찰', '검찰', '호우', '사건사고'],
    '경제': ['주식', '코인', '부동산', '금리', '환율', '기업', '투자', '증시', '경제', '시장', '무역', '유가', 'CPI', '재테크', '대출'],
    'IT/기술': ['AI', '반도체', '애플', '삼성', '구글', 'GitHub', '개발자', '스마트폰', '노트북', 'IT', '테크', '소프트웨어'],
    '엔터/방송': ['하이브', 'SM', 'JYP', 'YG', '아이돌', '컴백', '콘서트', '블랙핑크', 'BTS', '에스파', '뉴진스', '플레이브', '팬미팅', '시그널', '드라마', '영화', '배우', '시청률'],
    '스포츠': ['T1', '젠지', '페이커', 'LCK', '롤', 'e스포츠', '야구', '축구', '손흥민', '김하성', '키움', 'ssg', '한화', '올림픽'],
    '게임': ['게임', '신작', '업데이트', '리그오브레전드', '메이플', '로스트아크', '원신', '젠레스존제로', '스팀', '콘솔', 'PS5', '닌텐도'],
    '서브컬쳐': ['애니', '애니메이션', '라프텔', '주술회전', '최애의 아이', '극장판', '웹툰', '만화', '성우', '굿즈', '피규어', '팝업', '콜라보', '스텔라이브', '네네코마시로', '서코'],
    '커뮤니티/밈': ['밈', 'ㅋㅋ', '유행어', '챌린지', '커뮤', '논란', '드립', '더쿠', '에펨코리아', '디시인사이드', '속보', '근황']
}

# 데이터 수집 대상 사이트 정보
SITES = {
    "google_trends": {
        "type": "api" # Playwright 대신 pytrends 라이브러리 사용
    },
    "naver_news": {
        "type": "scrape",
        "url": "https://news.naver.com/main/ranking/popularDay.naver",
        "selector": "a.list_title"
    },
    "theqoo_hot": {
        "type": "scrape",
        "url": "https://theqoo.net/hot",
        "selector": "a.title"
    },
    "fmkorea_hot": {
        "type": "scrape",
        "url": "https://www.fmkorea.com/best",
        "selector": "h3.title a"
    },
    "dcinside_stellive": {
        "type": "scrape",
        "url": "https://gall.dcinside.com/mgallery/board/lists/?id=stellive",
        "selector": "td.gall_tit a.ub-word"
    },
    "dcinside_seoulcomic": {
        "type": "scrape",
        "url": "https://gall.dcinside.com/board/lists/?id=comic_new3",
        "selector": "td.gall_tit a.ub-word"
    },
    "dcinside_zenless": {
        "type": "scrape",
        "url": "https://gall.dcinside.com/mgallery/board/lists/?id=zenlesszonezero",
        "selector": "td.gall_tit a.ub-word"
    }
}

# 스크래핑 시 사용할 User-Agent 리스트
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
]

# 프록시 서버 리스트
PROXIES = []

# 각 작업 사이의 최소/최대 대기 시간 (초)
MIN_WAIT = 2
MAX_WAIT = 5
