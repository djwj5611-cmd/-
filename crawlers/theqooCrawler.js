// /crawlers/theqooCrawler.js
const createTheqooCrawler = (page) => async (keyword) => {
    await page.goto(`https://theqoo.net/index.php?mid=hot&search_target=title_content&search_keyword=${encodeURIComponent(keyword)}`);
    await page.waitForSelector('table.theqoo_hot_table td.title', { timeout: 15000 });

    const posts = await page.locator('table.theqoo_hot_table tr').all();
    const data = [];
    // 헤더(첫 번째 tr)를 제외하고 순회
    for (const post of posts.slice(1, 11)) {
        const titleElement = await post.locator('td.title a').first();
        const title = await titleElement.textContent().catch(() => '');
        const url = `https://theqoo.net${await titleElement.getAttribute('href').catch(() => '')}`;
        
        if (title && url) {
            data.push({
                title: title.trim(),
                url: url,
                content: '', // 더쿠는 목록에서 본문 내용을 제공하지 않음
                timestamp: new Date().toISOString()
            });
        }
    }
    return data;
};
module.exports = createTheqooCrawler;