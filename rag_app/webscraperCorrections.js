const fs = require('fs');
const path = require('path');

function calculateFiles() {
    const downloadDir = path.join(__dirname, 'downloads');
    let fileCount = 0;
    if (fs.existsSync(downloadDir)) {
        fileCount = fs.readdirSync(downloadDir).length;
    } else {
        console.warn(`Downloads directory not found: ${downloadDir}`);
    }
    console.log(`Number of files in downloads directory: ${fileCount}`);
    // Number of files in downloads directory: 3168
}

function calculateErrors() {
    const logFilePath = path.join(__dirname, 'webscraper.log');
    let logContent = '';
    let tickerCount = 0;
    let errorCount = 0;
    let tickersWithError = [];

    if (fs.existsSync(logFilePath)) {
        logContent = fs.readFileSync(logFilePath, 'utf8');
        // Use || [] to avoid errors if match returns null (e.g., empty log file)
        tickerCount = (logContent.match(/Completed processing ticker/g) || []).length;

        // Filter lines containing error indicators for a more accurate count
        const errorLines = logContent.split('\n').filter(line => line.includes('Error') || line.includes('No matching company found'));
        errorCount = errorLines.length;

        // Regex to capture the ticker symbol from known error formats
        // It looks for "Error processing ticker TICKER" (optional colon ignored) OR
        // "No matching company found for COMPANY_NAME (Ticker: TICKER)"
        // The ticker is captured in group 1 or group 2, excluding any trailing colon.
        const tickerRegex = /Error processing ticker ([^:\s]+):?|No matching company found for .* \(Ticker: (\S+)\)/;

        for (const line of errorLines) {
            const match = line.match(tickerRegex);
            if (match) {
                // The ticker will be in the first capturing group (match[1]) if the first part of the regex matched,
                // or in the second capturing group (match[2]) if the second part matched.
                const ticker = match[1] || match[2];
                if (ticker) {
                    tickersWithError.push(ticker);
                } else {
                    console.warn(`Regex matched but no ticker found in line: ${line}`);
                }
            } else {
                // Log lines that indicate an error but don't match the expected format
                console.warn(`Could not extract ticker using regex from line: ${line}`);
            }
        }
        // Remove duplicate tickers
        tickersWithError = [...new Set(tickersWithError)];

    } else {
        console.error(`Log file not found: ${logFilePath}`);
    }

    console.log(`Number of errors logged: ${errorCount}`);
    console.log(`Number of companies processed successfully: ${tickerCount}`);
    console.log(`Tickers with errors (${tickersWithError.length}): ${tickersWithError.length > 0 ? tickersWithError.join(', ') : 'None'}`);
    // Could not extract ticker using regex from line: [4/25/2025, 4:34:57 AM] Error downloading report for JCI:
    // Number of errors logged: 51
    // Number of companies processed successfully: 453
    // Tickers with errors (50): BRK-B, BAC, KO, RTX, PGR, BLK, PLTR, CRWD, ORLY, PCAR, FICO, PCG, MNST, NDAQ, KVUE, TRGP, 
    // SYY, DD, EFX, BRO, WTW, MPWR, LYV, K, NVR, DOV, SW, HBAN, CDW, WBD, ERIE, ZBRA, FOXA, INVH, LH, DRI, BF-B, VRSN, NWSA, 
    // DG, ALGN, EG, LNT, DOC, AMCR, EPAM, BXP, SMCI, SOLV, AMTM
}

function removeManuallyLocatedErrors() {
    // Webscraper downloaded wrong company's files for following 19 tickers
    // Number of companies processed successfully: 453 - 19 = 434
    const manuallyLocatedErrors = ['CE', 'ALLE', 'RL', 'POOL', 'MAS', 'L', 'J', 'SNA', 
        'KEY', 'STE', 'FE', 'PHM', 'K', 'ON', 'O', 'GEV', 'CI', 'GE', 'V']
    const downloadDir = path.join(__dirname, 'downloads');
    if (fs.existsSync(downloadDir)) {
        const files = fs.readdirSync(downloadDir);
        for (const file of files) {
            const ticker = file.split('_')[0];
            if (manuallyLocatedErrors.includes(ticker)) {
                fs.unlinkSync(path.join(downloadDir, file));
            }
        }
        const newFileCount = fs.readdirSync(downloadDir).length;
        console.log(`Number of files in downloads directory after removing manually located errors: ${newFileCount}`);
    } else {
        console.warn(`Downloads directory not found: ${downloadDir}`);
    }
    // Number of files in downloads directory after removing manually located errors: 3081
}

removeManuallyLocatedErrors();