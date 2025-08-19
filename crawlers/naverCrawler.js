
// /crawlers/naverCrawler.js
const createNaverCrawler = (page) => async (keyword) => {
    console.log(`[Naver News] Starting crawl for keyword: ${keyword}`);
    await page.goto(`https://search.naver.com/search.naver?where=news&query=${encodeURIComponent(keyword)}&sm=tab_opt&sort=0&photo=0&field=0&pd=0&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:all&is_sug_officeid=0`);
    await page.waitForSelector('.news_area', { timeout: 15000 });
    
    const newsItems = await page.locator('.news_area').all();
    const data = [];

    for (const item of newsItems.slice(0, 5)) { // 상위 5개 결과만 수집
        try {
            const title = await item.locator('.news_tit').textContent();
            const url = await item.locator('.news_tit').getAttribute('href');
            const content = await item.locator('.dsc_txt_wrap').textContent();
            
            data.push({
                source: 'Naver News',
                keyword,
                title: title.trim(),
                url,
                content: content.trim(),
                timestamp: new Date().toISOString()
            });
        } catch (e) {
            console.error(`[Naver News] Error processing an item for keyword '${keyword}': ${e.message}`);
        }
    }
    console.log(`[Naver News] Found ${data.length} items for keyword: ${keyword}`);
    return data;
};

module.exports = createNaverCrawler;
