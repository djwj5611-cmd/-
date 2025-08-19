// /crawlers/index.js
const createNaverCrawler = require('./naverCrawler');
const createTwitterCrawler = require('./twitterCrawler');
const createDcinsideCrawler = require('./dcinsideCrawler');
const createTheqooCrawler = require('./theqooCrawler'); // 추가

module.exports = {
    naver_news: createNaverCrawler,
    twitter: createTwitterCrawler,
    dcinside: createDcinsideCrawler,
    theqoo: createTheqooCrawler, // 추가
};