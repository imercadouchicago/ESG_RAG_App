const { chromium } = require('playwright');
const fs = require('fs');
const csv = require('csv-parser');
const path = require('path');

async function searchTickers() {
  const browser = await chromium.launch({
    headless: true  // Set to true for headless mode
  });
  
  // Create a new context with download permissions
  const context = await browser.newContext({
    acceptDownloads: true // Enable downloads
  });
  
  const page = await context.newPage();
  
  try {
    // Read and parse the CSV file
    const tickers = await new Promise((resolve, reject) => {
      const results = [];
      fs.createReadStream('data/SP500.csv')
        .pipe(csv())
        .on('data', (data) => {
          results.push(data[1]);
        })
        .on('end', () => {
          resolve(results);
        })
        .on('error', (error) => {
          reject(error);
        });
    });

    // Create downloads directory if it doesn't exist
    const downloadDir = path.join(__dirname, 'downloads');
    if (!fs.existsSync(downloadDir)) {
      fs.mkdirSync(downloadDir);
    }

    // Process each ticker
    for (const ticker of tickers) {
      try {
        // Navigate to the website
        await page.goto('https://responsibilityreports.com', {
          waitUntil: 'networkidle'
        });

        // Wait for the search input to be visible
        await page.waitForSelector('input[name="search"]');

        // Clear the input field (in case there's any existing text)
        await page.fill('input[name="search"]', '');

        // Type the ticker into the search field
        await page.fill('input[name="search"]', ticker);

        // Click the search button
        await page.click('input[type="submit"]');

        // Wait for search results page to load
        await page.waitForLoadState('networkidle');

        // Wait for and click the company name link
        await page.waitForSelector('span.companyName a');
        await page.click('span.companyName a');

        // Wait for the company page to load
        await page.waitForLoadState('networkidle');

        // Wait for the archived reports section
        await page.waitForSelector('div.archived_report_block');

        // Get all download links in the archived reports section
        const downloadLinks = await page.$$('span.btn_archived.download a');

        // Create company-specific directory
        const companyDir = path.join(downloadDir, ticker);
        if (!fs.existsSync(companyDir)) {
          fs.mkdirSync(companyDir);
        }

        // Download each report
        for (const downloadLink of downloadLinks) {
          try {
            // Start waiting for download before clicking
            const downloadPromise = page.waitForEvent('download');
            
            // Click the download link
            await downloadLink.click();
            
            // Wait for the download to start
            const download = await downloadPromise;
            
            // Get the suggested filename from the download
            const suggestedFilename = download.suggestedFilename();
            
            // Save file to company-specific directory
            const filePath = path.join(companyDir, suggestedFilename);
            await download.saveAs(filePath);
            
            console.log(`Successfully downloaded: ${suggestedFilename} for ${ticker}`);
            
            // Wait briefly between downloads
            await page.waitForTimeout(1000);
          } catch (downloadError) {
            console.error(`Error downloading report for ${ticker}:`, downloadError);
            continue;  // Continue with next download even if current one fails
          }
        }

        console.log(`Completed processing ticker: ${ticker}`);

        // Wait between companies
        await page.waitForTimeout(2000);

      } catch (error) {
        console.error(`Error processing ticker ${ticker}:`, error);
        continue;  // Continue with next ticker even if current one fails
      }
    }

  } catch (error) {
    console.error('Error:', error);
  } finally {
    // Close the browser
    await browser.close();
  }
}

// Run the script
searchTickers().catch(console.error);