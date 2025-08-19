
// /crawlers/twitterCrawler.js
const createTwitterCrawler = (page) => async (keyword) => {
    console.log(`[Twitter] Starting crawl for keyword: ${keyword}`);
    // "&f=live"는 실시간 트윗을 보기 위한 파라미터입니다.
    await page.goto(`https://x.com/search?q=${encodeURIComponent(keyword)}&f=live`);

    // Auth State가 만료되었는지 확인합니다. 로그인 페이지로 리디렉션되면 에러를 발생시킵니다.
    if (page.url().includes('/login')) {
        throw new Error('Twitter Auth State expired. Please re-generate auth_state.json');
    }

    await page.waitForSelector('article[data-testid="tweet"]', { timeout: 15000 });

    const articles = await page.locator('article[data-testid="tweet"]').all();
    const data = [];

    for (const article of articles.slice(0, 5)) { // 상위 5개 트윗만 수집
        try {
            const timeElement = article.locator('time').first();
            const timestamp = await timeElement.getAttribute('datetime');
            const postLink = await timeElement.locator('..').getAttribute('href');
            const url = `https://x.com${postLink}`;
            const content = await article.locator('div[lang]').textContent().catch(() => '');

            data.push({
                source: 'Twitter',
                keyword,
                title: content.substring(0, 70) + '...',
                url,
                content: content.trim(),
                timestamp
            });
        } catch (e) {
            console.error(`[Twitter] Error processing a tweet for keyword '${keyword}': ${e.message}`);
        }
    }
    console.log(`[Twitter] Found ${data.length} items for keyword: ${keyword}`);
    return data;
};

module.exports = createTwitterCrawler;
