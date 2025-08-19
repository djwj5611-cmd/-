// main_crawler.js
const { chromium } = require('playwright');
const fs = require('fs/promises');
const path = require('path');
const simpleGit = require('simple-git');
const { logToFile, notify } = require('./utils/logger');
const queue = require('./utils/pLimitQueue');
const { getProxyConfig } = require('./utils/proxyManager');
const crawlers = require('./crawlers');

const GIT_REPO_PATH = __dirname;
const REPORT_DIR = path.join(GIT_REPO_PATH, 'reports');
const KEYWORDS_FILE = path.join(GIT_REPO_PATH, 'data', 'keywords_for_js.json');
const AUTH_STATE_FILE = path.join(GIT_REPO_PATH, 'auth_state.json');

async function main() {
    await notify('Trend research process started.');
    let browser;
    const allCrawledData = [];
    const failedTasks = [];

    try {
        // 0. 준비 단계
        logToFile('Initializing...');
        await fs.mkdir(REPORT_DIR, { recursive: true });

        const keywords = JSON.parse(await fs.readFile(KEYWORDS_FILE, 'utf-8'));
        logToFile(`Keywords loaded: ${keywords.join(', ')}`);

        const launchOptions = {
            headless: true,
            proxy: getProxyConfig()
        };

        // 1. 인증 상태 로드
        let contextOptions = {};
        if (process.env.AUTH_STATE) {
            logToFile('AUTH_STATE secret found. Using it for browser context.');
            await fs.writeFile(AUTH_STATE_FILE, process.env.AUTH_STATE);
            contextOptions.storageState = AUTH_STATE_FILE;
        } else if (await fs.access(AUTH_STATE_FILE).then(() => true).catch(() => false)) {
            logToFile('Local auth_state.json found. Using it for browser context.');
            contextOptions.storageState = AUTH_STATE_FILE;
        } else {
            logToFile('No authentication state found. Proceeding without login.');
        }

        // 2. 브라우저 실행
        browser = await chromium.launch(launchOptions);
        const context = await browser.newContext(contextOptions);

        // 3. 크롤링 작업 생성
        const tasks = [];
        for (const source in crawlers) {
            for (const keyword of keywords) {
                tasks.push(queue(async () => {
                    let page;
                    try {
                        page = await context.newPage();
                        const crawlFunc = crawlers[source](page);
                        const data = await crawlFunc(keyword);
                        if (data.length > 0) {
                            allCrawledData.push(...data);
                        }
                        await page.close();
                    } catch (error) {
                        logToFile(`[ERROR] Failed to crawl ${source} for keyword "${keyword}": ${error.message}`);
                        failedTasks.push({ source, keyword, error: error.message });
                        if (page && !page.isClosed()) {
                            const screenshotPath = path.join(REPORT_DIR, `error_${source}_${keyword}.png`);
                            await page.screenshot({ path: screenshotPath });
                            logToFile(`Screenshot saved to ${screenshotPath}`);
                            await page.close();
                        }
                    }
                }));
            }
        }

        await Promise.all(tasks);

    } catch (error) {
        logToFile(`[FATAL] An unexpected error occurred: ${error.stack}`);
        await notify(`Trend research process failed with a fatal error: ${error.message}`);
    } finally {
        if (browser) {
            await browser.close();
            logToFile('Browser closed.');
        }
    }

    // 4. 리포트 생성 및 저장
    const reportContent = generateReport(allCrawledData);
    const date = new Date().toISOString().slice(0, 10);
    const reportFilePath = path.join(REPORT_DIR, `trend_report_${date}.md`);
    await fs.writeFile(reportFilePath, reportContent);
    logToFile(`Report saved to ${reportFilePath}`);

    // 5. Git에 결과 푸시
    await commitAndPush(reportFilePath);

    // 6. 최종 알림
    const summary = `Crawling finished. ${allCrawledData.length} items collected. ${failedTasks.length} tasks failed.`;
    logToFile(summary);
    await notify(`Trend research process finished. Report is available. ${summary}`);
}

function generateReport(data) {
    let report = `# Trend Report - ${new Date().toLocaleString('ko-KR')}\n\n`;
    const groupedBySource = data.reduce((acc, item) => {
        acc[item.source] = acc[item.source] || [];
        acc[item.source].push(item);
        return acc;
    }, {});

    for (const source in groupedBySource) {
        report += `## ${source}\n\n`;
        groupedBySource[source].forEach(item => {
            report += `### [${item.title}](${item.url})\n`;
            report += `*   **Keyword**: ${item.keyword}\n`;
            report += `*   **Timestamp**: ${item.timestamp}\n`;
            report += `*   **Content**: ${item.content.slice(0, 200)}...\n\n`;
        });
    }
    return report;
}

async function commitAndPush(filePath) {
    if (!process.env.GITHUB_TOKEN) {
        logToFile('GITHUB_TOKEN not found. Skipping git push.');
        return;
    }
    try {
        const git = simpleGit({ baseDir: GIT_REPO_PATH });
        await git.addConfig('user.name', 'github-actions[bot]');
        await git.addConfig('user.email', 'github-actions[bot]@users.noreply.github.com');
        
        await git.pull(); // 혹시 모를 충돌 방지를 위해 pull 먼저 실행
        await git.add(filePath);
        
        const status = await git.status();
        if (status.files.length > 0) {
            const commitMessage = `Update trend report for ${new Date().toISOString().slice(0, 10)}`;
            await git.commit(commitMessage);
            logToFile('Committing changes...');
            
            const remote = `https://${process.env.GITHUB_TOKEN}@github.com/${process.env.GITHUB_REPO}.git`;
            await git.push(remote, 'main'); // 'main' 브랜치에 푸시. 필요시 브랜치명 변경
            logToFile('Successfully pushed report to GitHub.');
        } else {
            logToFile('No changes to commit.');
        }
    } catch (error) {
        logToFile(`[ERROR] Failed to commit and push to GitHub: ${error.message}`);
        await notify(`Failed to push report to GitHub: ${error.message}`);
    }
}

main();
