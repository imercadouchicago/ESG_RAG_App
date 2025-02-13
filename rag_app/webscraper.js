const { chromium } = require('playwright');
const fs = require('fs');
const csv = require('csv-parser');
const path = require('path');

// Define the log file path
const logFilePath = path.join(__dirname, 'webscraper.log');

// Function to log messages
function logMessage(message) {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${message}\n`;
    
    // Append the log message to the file
    fs.appendFileSync(logFilePath, logEntry);
}

async function searchTickers() {
  const browser = await chromium.launch({headless: true});
  const context = await browser.newContext({acceptDownloads: true});
  const page = await context.newPage();
  logMessage("Browser and context initialized.");
  
  try {
    // Read and parse the CSV file
    const tickers = await new Promise((resolve, reject) => {
      const results = [];
      fs.createReadStream('data/SP500.csv')
        .pipe(csv({columns: true}))
        .on('data', (row) => {results.push(row.Symbol);})
        .on('end', () => {resolve(results);})
        .on('error', (error) => {reject(error);});
    });
    logMessage("CSV file read and parsed.");

    // Create downloads directory if it doesn't exist
    const downloadDir = path.join(__dirname, 'downloads');
    if (!fs.existsSync(downloadDir)) {
      fs.mkdirSync(downloadDir);
      logMessage("Downloads directory created.");
    }

    // Process each ticker
    for (const ticker of tickers) {
      try {
        logMessage(`Processing ticker: ${ticker}`);
        // Navigate to the website
        await page.goto('https://responsibilityreports.com', {waitUntil: 'networkidle'});

        // Wait for the search input to be visible
        const searchBar = 'input[name="search"][placeholder="Company or Ticker Symbol"]:visible';
        await page.waitForSelector(searchBar);

        // Clear the input field (in case there's any existing text)
        await page.fill(searchBar, '');

        // Type the ticker into the search field
        await page.fill(searchBar, ticker);

        // Click the search button
        const searchButton = 'input[type="submit"][value="Search"][aria-label="Submit button"]:visible';
        await page.click(searchButton);

        // Wait for search results page to load
        await page.waitForLoadState('networkidle');

        // Wait for and click the company name link
        await page.waitForSelector('span.companyName a');
        await page.click('span.companyName a');
        logMessage("Company name link found and clicked.");

        // Wait for the company page to load
        await page.waitForLoadState('networkidle');

        // Wait for the archived reports section
        await page.waitForSelector('div.archived_report_block');

        // Click the "Show older reports" button if it exists
        const showOlderReports = await page.$('div.show_older_reports');
        if (showOlderReports) {
          await showOlderReports.click();
          logMessage("Show older reports button clicked.");
          await page.waitForTimeout(3000);
        }

        // Get all download links in the archived reports section
        const fileNames = await page.$$('span.heading')
        const downloadLinks = await page.$$('span.btn_archived.download a', elements => elements.map(el => el.href));
        logMessage(`Found ${downloadLinks.length} download links and ${fileNames.length} filenames.`);

        // Download each report
        for (let i = 0; i < downloadLinks.length; i++) {
          try {
            let suggestedFilename;
            if (i+1 < fileNames.length) {
              // Get filename from heading if available
              const filenameElement = fileNames[i+1];
              const headingText = await filenameElement.textContent();
              suggestedFilename = `${ticker}_${headingText.trim()}.pdf`;
            } 

            // Check if file already exists
            const filePath = path.join(downloadDir, suggestedFilename);
            if (fs.existsSync(filePath)) {
              logMessage(`File already exists: ${suggestedFilename}`);
              continue;
            }

            // Start waiting for download before clicking
            const downloadPromise = page.waitForEvent('download');
            
            // Click the download link
            await downloadLinks[i].evaluate(el => el.click());
            
            // Wait for the download to start
            const download = await downloadPromise;
            
            // If we didn't get filename from heading, use download's suggested name
            if (!suggestedFilename) {
            suggestedFilename = `${ticker}_${download.suggestedFilename()}`;
            }
            
            // Save downloaded file to data directory
            await download.saveAs(filePath);
            logMessage(`Successfully downloaded: ${suggestedFilename} for ${ticker}`);
            
            // Wait briefly between downloads
            await page.waitForTimeout(1000);
          } catch (downloadError) {
            logMessage(`Error downloading report for ${ticker}:`, downloadError);
            continue;  // Continue with next download even if current one fails
          }
        }

        logMessage(`Completed processing ticker: ${ticker}`);

        // Wait between companies
        await page.waitForTimeout(2000);

      } catch (error) {
        logMessage(`Error processing ticker ${ticker}:`, error);
        console.error(`Error processing ticker ${ticker}:`, error);
        continue;  // Continue with next ticker even if current one fails
      }
    }

  } catch (error) {
    logMessage('Error:', error);
    console.error('Error:', error);
  } finally {
    // Close the browser
    await browser.close();
  }
}

// Run the script
searchTickers().catch(console.error);
const fileCount = fs.readdirSync(downloadDir).length;
logMessage(`Number of files in downloads directory: ${fileCount}`);