// /crawlers/naverCrawler.js
const createNaverCrawler = (page) => async (keyword) => {
    await page.goto(`https://search.naver.com/search.naver?where=news&sm=tab_jum&query=${encodeURIComponent(keyword)}`);

    // 더 안정적인 상위 컨테이너 선택자로 변경하고, 타임아웃을 30초로 늘림
    const newsContainerSelector = 'div.news_wrap';
    await page.waitForSelector(newsContainerSelector, { timeout: 30000 });
    
    // 랜덤 대기 추가
    await page.waitForTimeout(1000 + Math.random() * 1000);

    const newsItems = await page.locator(newsContainerSelector).all();
    const data = [];
    for (const item of newsItems.slice(0, 5)) {
        // 내부 선택자도 더 구체적으로 수정
        const title = await item.locator('a.news_tit').textContent().catch(() => '');
        const url = await item.locator('a.news_tit').getAttribute('href').catch(() => '');
        const content = await item.locator('.news_dsc .dsc_wrap a').textContent().catch(() => '');
        
        if (title && url) { // 제목과 URL이 있는 경우에만 추가
            data.push({
                title: title.trim(),
                url: url,
                content: content.trim(),
                timestamp: new Date().toISOString()
            });
        }
    }
    return data;
};
module.exports = createNaverCrawler;