@echo off
REM TrendMasterV3 실행 스크립트
REM 이 스크립트는 Docker를 사용하여 트렌드 분석을 수행합니다.

ECHO [Step 1/3] Docker가 실행 중인지 확인합니다...
docker ps > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO [Error] Docker가 실행되고 있지 않습니다.
    ECHO Docker Desktop을 시작하고 다시 시도해주세요.
    pause
    exit /b 1
)
ECHO [Success] Docker가 활성화되어 있습니다.
ECHO.

ECHO [Step 2/3] TrendMasterV3 Docker 이미지를 빌드합니다. (최초 실행 시 시간이 걸릴 수 있습니다)
docker build -t trendmaster-v3 .
IF %ERRORLEVEL% NEQ 0 (
    ECHO [Error] Docker 이미지 빌드에 실패했습니다.
    ECHO Dockerfile 또는 네트워크 연결을 확인해주세요.
    pause
    exit /b 1
)
ECHO [Success] 이미지 빌드 완료.
ECHO.

ECHO [Step 3/3] 트렌드 분석 컨테이너를 실행합니다.
ECHO 이 작업은 몇 분 정도 소요될 수 있습니다. 잠시만 기다려주세요...
ECHO.

REM results 폴더가 없으면 생성
IF NOT EXIST .\results (
    mkdir .\results
)

REM Docker 컨테이너 실행.
REM --rm : 컨테이너 종료 시 자동으로 삭제
REM -v "%cd%\results:/app/results" : 로컬의 results 폴더와 컨테이너의 results 폴더를 연결
docker run --rm -v "%cd%\results:/app/results" trendmaster-v3

ECHO.
ECHO [Complete] 모든 작업이 완료되었습니다.
ECHO 'results' 폴더에서 생성된 리포트 파일을 확인하세요.
pause
