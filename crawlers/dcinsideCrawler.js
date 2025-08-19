// /crawlers/dcinsideCrawler.js
const createDcinsideCrawler = (page) => async (keyword) => {
    await page.goto(`https://search.dcinside.com/post/p/1?q=${encodeURIComponent(keyword)}`);
    await page.waitForSelector('.sch_result_list > li', { timeout: 15000 });

    const posts = await page.locator('.sch_result_list > li').all();
    const data = [];
    for (const post of posts.slice(0, 10)) {
        const title = await post.locator('.tit_txt').textContent().catch(() => '');
        const url = await post.locator('.tit_txt').getAttribute('href').catch(() => '');
        const content = await post.locator('.link_dsc_txt').textContent().catch(() => '');
        
        if (title && url) {
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
module.exports = createDcinsideCrawler;