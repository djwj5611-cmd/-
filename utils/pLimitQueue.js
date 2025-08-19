
// /utils/pLimitQueue.js
const pLimit = require('p-limit');

// 동시 실행 3개로 제한. 사이트 차단을 피하기 위해 너무 높게 설정하지 않는 것이 중요.
const queue = pLimit(3); 

module.exports = queue;
