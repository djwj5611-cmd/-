
// /utils/proxyManager.js
require('dotenv').config();

function getProxyConfig() {
    const proxyList = (process.env.PROXY_LIST || '').split(',').filter(p => p.trim());
    if (proxyList.length === 0) {
        return null; // 프록시 목록이 없으면 null 반환
    }
    
    // 프록시 목록에서 무작위로 하나 선택
    const proxy = proxyList[Math.floor(Math.random() * proxyList.length)].trim();
    
    // 로그에는 비밀번호 등 민감 정보가 노출되지 않도록 호스트 부분만 출력
    try {
        const url = new URL(proxy);
        console.log(`  Using proxy: ${url.hostname}:${url.port}`);
    } catch (e) {
        console.log(`  Using proxy: (format error)`);
    }
    
    return { server: proxy };
}

module.exports = { getProxyConfig };
