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
                    'category_name': scraper.category_name,
                    'products': scraper.products
                }
            finally:
                driver_manager.quit()
                
        except Exception as e:
            logger.error(f"Error scraping category {category_url}: {str(e)}")
            return {
                'url': category_url,
                'success': False,
                'category_name': None,
                'products': []
            }

    @staticmethod
    def scrape_product(args):
        """单个产品的爬取函数"""
        product_url, category_name = args
        try:
            driver_manager = DriverManager()
            driver_manager.setup_driver(ScraperConfig.HEADLESS)
            scraper = AmazonScraper(driver_manager)
            scraper.category_name = category_name
            
            try:
                product_info = scraper.extract_product_info(product_url)
                return product_info if product_info else None
            finally:
                driver_manager.quit()
                
        except Exception as e:
            logger.error(f"Error scraping product {product_url}: {str(e)}")
            return None

    def run_parallel(self, category_urls):
        """并行爬取多个类别"""
        start_time = time.time()
        results = []
        
        # 第一步：并行获取每个类别的产品链接
        with Pool(self.max_workers) as pool:
            category_results = pool.map(self.scrape_category, category_urls)
            
        # 收集所有产品URL和对应的类别名称
        product_tasks = []
        for result in category_results:
            if result['success'] and result['products']:
                category_name = result['category_name']
                product_tasks.extend([(url, category_name) for url in result['products']])
        
        # 第二步：并行爬取所有产品详情
        if product_tasks:
            with Pool(self.max_workers) as pool:
                product_results = pool.map(self.scrape_product, product_tasks)
                # 过滤掉None结果
                product_results = [p for p in product_results if p]
                
            # 按类别组织结果并保存
            from collections import defaultdict
            category_products = defaultdict(list)
            for product in product_results:
                if product:
                    category_products[product['category']].append(product)
                    
            # 保存每个类别的结果
            from data_saver import DataSaver
            for category, products in category_products.items():
                if products:
                    DataSaver.save_to_excel(products, category)
        
        end_time = time.time()
        logger.info(f"\nParallel scraping completed in {end_time - start_time:.2f} seconds")
        logger.info(f"Total categories attempted: {len(category_urls)}")
        logger.info(f"Successfully scraped products: {len(product_results) if product_tasks else 0}")
        
        return category_results