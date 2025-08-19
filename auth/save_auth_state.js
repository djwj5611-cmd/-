// /auth/save_auth_state.js
const { chromium } = require('playwright');
const fs = require('fs');
require('dotenv').config(); // .env 파일 로드

(async () => {
    console.log('Launching browser for manual login...');
    const browser = await chromium.launch({ headless: false }); // 브라우저 창을 띄웁니다.
    const context = await browser.newContext();
    const page = await context.newPage();

    try {
        console.log('Navigating to Twitter login page. Please log in manually in the opened browser window.');
        await page.goto('https://x.com/login');

        // 사용자에게 로그인할 시간을 줍니다 (3분 = 180초)
        console.log('You have 3 minutes to log in. Please complete the login process in the browser.');
        
        // 사용자가 로그인하여 홈 페이지로 이동할 때까지 기다립니다.
        // 3분(180000ms) 동안 기다리며, 홈 페이지로 이동하면 다음 단계로 넘어갑니다.
        await page.waitForURL('https://x.com/home', { timeout: 180 * 1000 }); 

        console.log('Login detected. Saving authentication state...');

        // 인증 상태 저장
        const authState = await context.storageState();
        fs.writeFileSync('auth_state.json', JSON.stringify(authState, null, 2));
        console.log('\nSuccessfully created auth_state.json!');
        console.log('Please copy the content of this file and add it to your GitHub repository secrets with the name AUTH_STATE.');

    } catch (error) {
        console.error('\nAn error occurred during manual login process:', error);
        console.error('Please ensure you logged in successfully within the given time.');
    } finally {
        if (browser) {
            await browser.close();
            console.log('Browser closed.');
        }
    }
})();
