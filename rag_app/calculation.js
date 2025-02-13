const fs = require('fs');
const path = require('path');

const downloadDir = path.join(__dirname, 'downloads');
const fileCount = fs.readdirSync(downloadDir).length;
console.log(`Number of files in downloads directory: ${fileCount}`);

const logFilePath = path.join(__dirname, 'webscraper.log');
const logContent = fs.readFileSync(logFilePath, 'utf8');
const tickerCount = logContent.match(/Completed processing ticker/g).length;
const errorCount = logContent.match(/Error/g).length;
console.log(`Number of errors: ${errorCount}`);
console.log(`Number of companies processed without error: ${tickerCount}`);
