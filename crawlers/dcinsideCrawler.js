
// /crawlers/dcinsideCrawler.js
// TODO: DCInside 크롤러 로직 구현 필요
const createDcinsideCrawler = (page) => async (keyword) => {
    console.log(`[DCInside] Crawling for '${keyword}' is not implemented yet.`);
    // 1. DCInside 검색 페이지로 이동
    // 2. 검색 결과 목록 선택자 대기
    // 3. 목록 순회하며 제목, 링크, 내용, 시간 등 추출
    // 4. 표준화된 데이터 객체 배열로 반환
    return []; // 임시로 빈 배열 반환
};
module.exports = createDcinsideCrawler;
