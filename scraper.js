const fs = require('fs');
const puppeteer = require('puppeteer');
const readline = require('readline');

async function extractEpisodeURLs(showURL, numEpisodes) {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto(showURL);

    const episodeURLs = [];

    while (true) {
        // Extract the episode URLs from the current page
        const currentEpisodeURLs = await page.$$eval('a.normalisedLink', links =>
            links.map(link => link.href)
        );

        // Filter for URLs that match the specific pattern
        const filteredEpisodeURLs = currentEpisodeURLs.filter(url => {
            return url.startsWith('https://www.amazon.in/minitv/tp/');
        });

        episodeURLs.push(...filteredEpisodeURLs);

        // If we've collected enough episode URLs, break the loop
        if (episodeURLs.length >= numEpisodes) break;

        // Scroll down to load more content if available
        const loadMoreButton = await page.$('.load-more-button');
        if (!loadMoreButton) break; // No more content to load

        await loadMoreButton.click();
        await page.waitForTimeout(2000); // Wait for content to load (adjust as needed)
    }

    await browser.close();

    return episodeURLs.slice(0, numEpisodes);
}

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.question('Enter the URL of the show you want to extract episode URLs from: ', (showURL) => {
    rl.question('Enter the number of episodes to scrape: ', (numEpisodesToScrape) => {
        rl.close();

        numEpisodesToScrape = parseInt(numEpisodesToScrape, 10);

        if (!isNaN(numEpisodesToScrape)) {
            extractEpisodeURLs(showURL, numEpisodesToScrape).then(episodeURLs => {
                console.log('Episode URLs extracted:');
                episodeURLs.forEach(url => console.log(url));

                // Save the episode URLs to a text file
                fs.writeFileSync('episode_urls.txt', episodeURLs.join('\n'), 'utf-8');
            }).catch(error => {
                console.error('Error:', error);
            });
        } else {
            console.error('Invalid input. Please enter a valid number of episodes to scrape.');
        }
    });
});
