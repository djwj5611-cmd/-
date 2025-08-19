// /utils/logger.js
const fs = require('fs');
const path = require('path');
const https = require('https');
require('dotenv').config();

const logFilePath = path.join(__dirname, '..', 'crawler.log');

function logToFile(message) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}\n`;
    console.log(logMessage.trim());
    fs.appendFileSync(logFilePath, logMessage);
}

async function notify(message) {
    logToFile(`[Notification] ${message}`);
    const webhookUrl = process.env.SLACK_WEBHOOK_URL;
    if (!webhookUrl) {
        return;
    }

    const payload = JSON.stringify({ text: message });
    const options = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Content-Length': payload.length }
    };

    return new Promise((resolve) => {
        const req = https.request(webhookUrl, options, res => {
            if (res.statusCode !== 200) {
                logToFile(`Slack notification failed with status code: ${res.statusCode}`);
            }
            resolve();
        });
        req.on('error', e => {
            logToFile(`Slack notification request error: ${e.message}`);
            resolve();
        });
        req.write(payload);
        req.end();
    });
}

module.exports = { notify, logToFile };
