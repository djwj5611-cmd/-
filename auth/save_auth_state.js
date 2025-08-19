// /auth/save_auth_state.js
const { chromium } = require('playwright');
const fs = require('fs');
require('dotenv').config(); // .env 파일에서 환경 변수 로드

(async () => {
    const { TWITTER_ID, TWITTER_PW } = process.env;
    if (!TWITTER_ID || !TWITTER_PW) {
        console.error('Error: TWITTER_ID and TWITTER_PW must be set in .env file.');
        return;
    }

    console.log('Launching browser to generate auth state...');
    const browser = await chromium.launch({ headless: false }); // 헤드리스 모드 해제하여 로그인 과정 확인
    const context = await browser.newContext();
    const page = await context.newPage();

    try {
        console.log('Navigating to Twitter login page...');
        await page.goto('https://x.com/login');

        // 아이디 입력
        console.log('Entering Twitter ID...');
        await page.locator('input[name="text"]').fill(TWITTER_ID);
        await page.getByRole('button', { name: '다음' }).click();

        // 비밀번호 입력
        console.log('Entering Twitter password...');
        await page.locator('input[name="password"]').fill(TWITTER_PW);
        await page.getByRole('button', { name: '로그인' }).click();

        // 로그인 성공 확인 (타임라인 로딩 대기)
        console.log('Waiting for timeline to load...');
        await page.waitForURL('https://x.com/home', { timeout: 60000 });
        console.log('Login successful!');

        // 인증 상태 저장
        const authState = await context.storageState();
        fs.writeFileSync('auth_state.json', JSON.stringify(authState, null, 2));
        console.log('\nSuccessfully created auth_state.json!');
        console.log('Please copy the content of this file and add it to your GitHub repository secrets with the name AUTH_STATE.');

    } catch (error) {
        console.error('\nAn error occurred during authentication:', error);
        console.error('Please check your credentials in .env file and try again.');
    } finally {
        await browser.close();
        console.log('Browser closed.');
    }
})();
