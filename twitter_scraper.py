from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
from datetime import datetime, timedelta, timezone
import json
import os
import pickle

class TwitterSearchBot:
    def __init__(self):
        base_keywords = ["스텝", "스태프", "직원", "팀원", "팀", "매니저"]
        action_keywords = ["공고", "구인", "채용", "모집"]
        self.keywords = [f"{base} {action}" for base in base_keywords for action in action_keywords]
        
        self.driver = None
        self.wait = None
        
        self.save_dir = "twitter_reports"
        os.makedirs(self.save_dir, exist_ok=True)

        # GitHub Actions Secrets에서 로그인 정보 가져오기
        self.username = os.environ.get("TWITTER_USER")
        self.password = os.environ.get("TWITTER_PASSWORD")
        self.email = os.environ.get("TWITTER_EMAIL")

    def start_driver(self):
        """Chrome 브라우저 실행 및 자동 로그인"""
        try:
            print("Chrome 브라우저로 실행을 시도합니다...")
            
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--log-level=3')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            self.driver = webdriver.Chrome(service=Service(), options=options)
            self.wait = WebDriverWait(self.driver, 15) # 대기 시간 증가
            
            self.handle_login()
            return True

        except Exception as e:
            print(f"Chrome 브라우저 실행에 실패했습니다: {e}")
            return False

    def handle_login(self):
        """GitHub Secrets와 WebDriverWait를 이용한 안정적인 로그인 처리"""
        if not all([self.username, self.password]):
            raise ValueError("트위터 아이디 또는 비밀번호가 설정되지 않았습니다. GitHub Secrets를 확인해주세요.")

        try:
            print("트위터 로그인 페이지로 이동합니다: https://x.com/login")
            self.driver.get("https://x.com/login")
            
            # 1. 아이디(username) 입력창이 나타날 때까지 최대 15초 기다림
            print("아이디 입력창을 기다립니다...")
            username_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='text']"))
            )
            username_input.send_keys(self.username)
            print("아이디를 입력했습니다.")
            
            # '다음' 버튼 클릭
            next_button = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Next')]")
            next_button.click()
            print("'다음' 버튼을 클릭했습니다.")
            
            # 2. 비밀번호(password) 입력창이 나타날 때까지 최대 15초 기다림
            print("비밀번호 입력창을 기다립니다...")
            password_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
            )
            password_input.send_keys(self.password)
            print("비밀번호를 입력했습니다.")

            # '로그인' 버튼 클릭
            login_button = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Log in')]")
            login_button.click()
            print("'로그인' 버튼을 클릭했습니다.")

            # 로그인 후 타임라인(Home) 링크가 보일 때까지 대기 (성공 확인용)
            print("로그인 성공 확인 중...")
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[@data-testid='AppTabBar_Home_Link']"))
            )
            print("로그인에 성공했습니다!")

        except Exception as e:
            print(f"로그인 과정에서 오류가 발생했습니다: {e}")
            # 실패 시 스크린샷을 찍어두면 디버깅에 매우 유용합니다.
            screenshot_path = "login_failed.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"'{screenshot_path}' 이름으로 실패 화면을 저장했습니다.")
            raise Exception("Login failed")

    def search_keyword(self, keyword):
        """키워드와 'since:' 연산자를 사용해 24시간 내 트윗만 검색"""
        print(f"\n'{keyword}' 검색 중...")
        
        # 검색 시작 날짜를 'YYYY-MM-DD' 형식으로 계산
        since_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 트위터 검색 URL에 since:{날짜} 추가
        search_url = f"https://twitter.com/search?q={keyword}%20since%3A{since_date}&src=typed_query&f=live"
        
        print(f"  -> 요청 URL: {search_url}") # 디버깅을 위해 URL 출력
        self.driver.get(search_url)
        time.sleep(4)
        
        results = []
        processed_links = set()
        
        for _ in range(5): # 최대 5번 스크롤
            tweets = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            
            for tweet in tweets:
                try:
                    tweet_data = self.extract_tweet_info(tweet)
                    # since 연산자로 이미 필터링했으므로, 중복만 확인
                    if tweet_data and tweet_data['link'] not in processed_links:
                        tweet_data['keyword'] = keyword
                        results.append(tweet_data)
                        processed_links.add(tweet_data['link'])
                        print(f"  -> 새 게시글 발견: {tweet_data['text'][:40]}...")
                except Exception:
                    continue
            
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
        return results

    def extract_tweet_info(self, tweet_element):
        """트윗 정보 추출"""
        try:
            text = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]').text
            post_time = tweet_element.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
            user_info = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]').text.split('\n')
            username = user_info[0] if user_info else "Unknown"
            
            link_element = tweet_element.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]')
            tweet_link = link_element.get_attribute('href')

            return {
                'text': text, 'time': post_time, 'username': username,
                'link': tweet_link,
                'timestamp': datetime.fromisoformat(post_time.replace('Z', '+00:00'))
            }
        except Exception:
            return None

    def run(self):
        """전체 검색 실행"""
        if not self.start_driver():
            print("드라이버 시작에 실패하여 검색을 중단합니다.")
            return

        all_results = []
        try:
            for keyword in self.keywords:
                results = self.search_keyword(keyword)
                all_results.extend(results)
                time.sleep(2)
        finally:
            if self.driver:
                self.driver.quit()
        
        self.save_results(all_results)

    def save_results(self, results):
        """결과 저장"""
        if not results:
            print("\n24시간 이내 새로운 게시글을 찾지 못했습니다.")
            return
            
        unique_results = {r['link']: r for r in results}.values()
        sorted_results = sorted(list(unique_results), key=lambda x: x['timestamp'], reverse=True)
        
        print(f"\n총 {len(sorted_results)}개의 새로운 게시글을 찾았습니다!")
        
        today_date = datetime.now().strftime('%Y-%m-%d')
        file_name = f"{today_date}_트위터 리서치.txt"
        full_path = os.path.join(self.save_dir, file_name)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(f"=== 트위터 스태프 모집 검색 결과 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===\n")
            f.write(f"총 {len(sorted_results)}개 발견\n\n")
            for i, result in enumerate(sorted_results, 1):
                f.write(f"[{i}] 검색 키워드: {result['keyword']}\n")
                f.write(f"작성자: {result['username']}\n")
                f.write(f"시간: {result['timestamp'].strftime('%Y-%m-%d %H:%M')}\n")
                f.write(f"내용: {result['text']}\n")
                f.write(f"링크: {result['link']}\n")
                f.write("-" * 70 + "\n\n")
        
        print(f"결과가 {full_path} 파일에 저장되었습니다.")
        
        print("\n--- 최근 3개 미리보기 ---")
        for i, result in enumerate(sorted_results[:3], 1):
            username_for_print = result['username'].encode('ascii', 'ignore').decode('ascii')
            print(f"\n{i}. [{result['keyword']}] {username_for_print}")
            print(f"   {result['text'][:80]}...")
            print(f"   링크: {result['link']}")

if __name__ == "__main__":
    bot = TwitterSearchBot()
    bot.run()
