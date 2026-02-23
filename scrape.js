const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    let totalSum = 0;

    const seeds = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16];

    for (const seed of seeds) {
        const url = `https://sanand0.github.io/tdsdata/js_table/?seed=${seed}`;
        console.log(`Processing: ${url}`);
        try {
            await page.goto(url, { waitUntil: 'networkidle' });

            // Wait for table content to be rendered
            await page.waitForSelector('table', { timeout: 10000 });

            // Extract all numeric values from table cells
            const values = await page.$$eval('td', tds =>
                tds.map(td => td.innerText.trim())
            );

            let pageSum = 0;
            for (const val of values) {
                // Remove commas and try parsing as float
                const num = parseFloat(val.replace(/,/g, ''));
                if (!isNaN(num)) {
                    pageSum += num;
                }
            }
            console.log(`Sum for seed ${seed}: ${pageSum}`);
            totalSum += pageSum;
        } catch (error) {
            console.error(`Error processing seed ${seed}: ${error.message}`);
        }
    }

    console.log(`========================================`);
    console.log(`TOTAL SUM: ${totalSum}`);
    console.log(`========================================`);

    await browser.close();
})();
