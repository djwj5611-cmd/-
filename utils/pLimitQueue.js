// /utils/pLimitQueue.js

// p-limit 최신 버전(ESM-only)과 이전 버전(CommonJS) 모두에서
// CommonJS require로 안전하게 사용 가능하도록 수정
const pLimit = require('p-limit').default || require('p-limit');

const MAX_CONCURRENT_CRAWLERS = 3; // 동시 실행 수 제한

const queue = pLimit(MAX_CONCURRENT_CRAWLERS);

module.exports = queue;