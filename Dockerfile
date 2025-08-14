# 1. 기본 이미지 설정 (Python 3.11 슬림 버전)
FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 파일 복사
COPY requirements.txt .

# 4. Python 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 나머지 소스 코드 복사
COPY . .

# 6. 스크립트 실행
CMD ["python", "main.py"]
