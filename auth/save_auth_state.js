// /auth/save_auth_state.js
const { chromium } = require('playwright');
const fs = require('fs');
require('dotenv').config(); // .env 파일 로드

(async () => {
    const { TWITTER_ID, TWITTER_PW, GOOGLE_ID, GOOGLE_PW } = process.env;

    if (!TWITTER_ID && !GOOGLE_ID) {
        console.error('Error: Either TWITTER_ID/TWITTER_PW or GOOGLE_ID/GOOGLE_PW must be set in .env file.');
        return;
    }

    console.log('Launching browser to generate auth state...');
    const browser = await chromium.launch({ headless: false }); // 헤드리스 모드 해제하여 로그인 과정 확인
    const context = await browser.newContext();
    const page = await context.newPage();

    try {
        console.log('Navigating to Twitter login page...');
        await page.goto('https://x.com/login');

        if (GOOGLE_ID && GOOGLE_PW) {
            console.log('Attempting Google login...');
            
            // 'Google로 로그인' 또는 'Sign in with Google' 버튼 찾기 및 클릭
            let googleLoginButton;
            try {
                googleLoginButton = await page.locator('button:has-text("Google로 로그인"), button:has-text("Sign in with Google"), div[data-provider="google"] button').first();
                await googleLoginButton.waitFor({ state: 'visible', timeout: 10000 });
                await googleLoginButton.click();
                console.log('Clicked Google login button.');
            } catch (e) {
                console.warn('Could not find or click Google login button directly. Trying alternative.');
                // 직접 버튼을 찾지 못했을 경우, ID/PW 입력 필드에 더미 값을 넣어 다음 화면으로 이동 후 구글 옵션 찾기 시도
                await page.locator('input[name="text"]').fill('dummy'); 
                await page.getByRole('button', { name: '다음' }).click();
                try {
                    const googleOption = await page.locator('button:has-text("Google 계정으로 로그인")').first();
                    await googleOption.waitFor({ state: 'visible', timeout: 5000 });
                    await googleOption.click();
                    console.log('Clicked Google account option on next screen.');
                } catch (e2) {
                    console.error('Could not find Google login option after initial attempt. Please check Twitter UI.');
                    throw new Error('Google login button/option not found.');
                }
            }

            // 구글 로그인 페이지/팝업 대기
            await page.waitForURL(/accounts.google.com/, { timeout: 30000 });
            console.log('Navigated to Google login page.');

            // 구글 ID 입력
            console.log('Entering Google ID...');
            await page.locator('input[type="email"]').fill(GOOGLE_ID);
            await page.locator('button:has-text("다음"), div[role="button"]:has-text("다음")').click(); // '다음' 버튼

            // 구글 비밀번호 입력
            console.log('Entering Google password...');
            await page.locator('input[type="password"]').fill(GOOGLE_PW);
            await page.locator('button:has-text("다음"), div[role="button"]:has-text("다음")').click(); // '다음' 버튼

            // 트위터 홈으로 리디렉션 대기
            await page.waitForURL('https://x.com/home', { timeout: 60000 });
            console.log('Google login successful, redirected to Twitter!');

        } else if (TWITTER_ID && TWITTER_PW) {
            console.log('Attempting direct Twitter login...');
            // 기존 트위터 직접 로그인 로직
            await page.locator('input[name="text"]').fill(TWITTER_ID);
            await page.getByRole('button', { name: '다음' }).click();
            await page.locator('input[name="password"]').fill(TWITTER_PW);
            await page.getByRole('button', { name: '로그인' }).click();
            await page.waitForURL('https://x.com/home', { timeout: 60000 });
            console.log('Direct Twitter login successful!');
        } else {
            throw new Error('No valid login credentials (Twitter or Google) provided in .env file.');
        }

        // 인증 상태 저장
        const authState = await context.storageState();
        fs.writeFileSync('auth_state.json', JSON.stringify(authState, null, 2));
        console.log('\nSuccessfully created auth_state.json!');
        console.log('Please copy the content of this file and add it to your GitHub repository secrets with the name AUTH_STATE.');

    } catch (error) {
        console.error('\nAn error occurred during authentication:', error);
        console.error('Please check your credentials in .env file and ensure the login flow matches the script\'s expectations.');
        console.error('If the Twitter/Google UI has changed, the selectors in the script may need updating.');
    } finally {
        await browser.close();
        console.log('Browser closed.');
    }
})();