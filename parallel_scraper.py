import multiprocessing as mp
from multiprocessing import Pool
from driver_manager import DriverManager
from scraper import AmazonScraper
from logger import logger
import time
from config import ScraperConfig


class ParallelScraper:
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or mp.cpu_count()

    @staticmethod
    def scrape_category(category_url):
        """单个类别的爬取函数"""
        try:
            driver_manager = DriverManager()
            driver_manager.setup_driver(ScraperConfig.HEADLESS)
            scraper = AmazonScraper(driver_manager)

            try:
                success = scraper.run(category_url)
                return {
                    'url': category_url,
                    'success': success,
                    'category_name': scraper.category_name
                }
            finally:
                driver_manager.quit()

        except Exception as e:
            logger.error(f"Error scraping category {category_url}: {str(e)}")
            return {
                'url': category_url,
                'success': False,
                'category_name': None
            }

    def run_parallel(self, category_urls):
        """并行爬取多个类别"""
        start_time = time.time()

        # 并行获取每个类别的产品
        with Pool(self.max_workers) as pool:
            category_results = pool.map(self.scrape_category, category_urls)

        end_time = time.time()
        logger.info(f"\nParallel scraping completed in {end_time - start_time:.2f} seconds")
        logger.info(f"Total categories attempted: {len(category_urls)}")

        # 统计成功抓取的类别数
        successful = sum(1 for r in category_results if r['success'])
        logger.info(f"Successfully scraped categories: {successful}")

        return category_results