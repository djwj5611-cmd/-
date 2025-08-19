
// /crawlers/index.js
const createNaverCrawler = require('./naverCrawler');
const createTwitterCrawler = require('./twitterCrawler');
const createDcinsideCrawler = require('./dcinsideCrawler');
const createTheqooCrawler = require('./theqooCrawler');

// 각 크롤러 생성 함수를 객체로 묶어 내보냅니다.
// main_crawler.js에서 이 객체를 사용하여 필요한 크롤러를 동적으로 선택합니다.
module.exports = {
    'naver_news': createNaverCrawler,
    'twitter': createTwitterCrawler,
    'dcinside': createDcinsideCrawler,
    'theqoo': createTheqooCrawler,
};
