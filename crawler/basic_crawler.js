import { PuppeteerCrawler } from 'crawlee';
import puppeteerExtra from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';

// Add stealth plugin
puppeteerExtra.use(StealthPlugin());

async function main() {
    const crawler = new PuppeteerCrawler({
        async requestHandler({ page, request, log, enqueueLinks, pushData }) {
            log.info(`Visiting ${request.url}`);

            // Wait for listings to load
            await page.waitForSelector('li[data-listing-id]');

            // Extract product info
            const products = await page.$$eval('li[data-listing-id]', (items) =>
                items.map((el) => {
                    const titleEl = el.querySelector('h3');
                    const title = titleEl ? titleEl.innerText.trim() : 'No title';

                    const priceEl = el.querySelector('span.currency-value');
                    const price = priceEl ? priceEl.innerText.trim() : 'No price';

                    const ratingEl = el.querySelector('span.screen-reader-only');
                    let rating = '';
                    if (ratingEl) {
                        const match = ratingEl.innerText.match(/(\d+(\.\d+)?)/);
                        rating = match ? match[1] : '';
                    }

                    const reviewsEl = el.querySelector('span.text-body-smaller');
                    const reviews = reviewsEl ? reviewsEl.innerText.trim() : '';

                    const urlEl = el.querySelector('a');
                    const url = urlEl ? urlEl.href : '';

                    return { title, price, rating, reviews, url };
                })
            );

            if (products.length === 0) {
                log.info('No products found.');
                return;
            }

            // Log and save all products
            for (const product of products) {
                log.info(`Product: ${product.title} | Price: ${product.price} | Rating: ${product.rating} | Reviews: ${product.reviews} | URL: ${product.url}`);
                await pushData(product);
            }
        },
    });

    await crawler.run(['https://www.etsy.com/search?q=cat+art+shirts']);
}

main().catch((error) => {
    console.error('Crawler failed:', error);
    process.exit(1);
});
