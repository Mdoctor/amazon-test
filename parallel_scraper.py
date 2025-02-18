import multiprocessing as mp
from multiprocessing import Pool
from driver_manager import DriverManager
from scraper import AmazonScraper
from logger import logger
import time
from config import ScraperConfig
from tqdm import tqdm
from finalExcel import process_excel
from data_saver import DataSaver


class ParallelScraper:
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or mp.cpu_count()
        logger.info(f"Initializing parallel scraper with {self.max_workers} workers")

    @staticmethod
    def scrape_category(category_url):
        """单个类别的爬取函数"""
        process_name = mp.current_process().name
        logger.info(f"Process {process_name} starting to scrape: {category_url}")

        try:
            driver_manager = DriverManager()
            driver_manager.setup_driver(ScraperConfig.HEADLESS)
            scraper = AmazonScraper(driver_manager)

            try:
                start_time = time.time()
                scrape_result = scraper.run(category_url)
                execution_time = time.time() - start_time

                # 如果爬取成功且有保存的文件路径，处理Excel文件
                if scrape_result['success'] and scrape_result['saved_file_path']:
                    # 处理Excel文件并保存到最终目录
                    final_output_path = process_excel(
                        scrape_result['saved_file_path'],
                        DataSaver.FINAL_OUTPUT_DIR
                    )
                else:
                    final_output_path = None

                result = {
                    'url': category_url,
                    'success': scrape_result['success'],
                    'category_name': scrape_result['category_name'],
                    'execution_time': execution_time,
                    'process_name': process_name,
                    'initial_file_path': scrape_result.get('saved_file_path'),
                    'final_file_path': final_output_path
                }

                logger.info(f"Process {process_name} completed scraping: {category_url} "
                          f"(Success: {scrape_result['success']}, Time: {execution_time:.2f}s)")
                if final_output_path:
                    logger.info(f"Final output saved to: {final_output_path}")

                return result

            finally:
                driver_manager.quit()

        except Exception as e:
            logger.error(f"Process {process_name} error scraping {category_url}: {str(e)}")
            return {
                'url': category_url,
                'success': False,
                'category_name': None,
                'execution_time': 0,
                'process_name': process_name,
                'error': str(e),
                'initial_file_path': None,
                'final_file_path': None
            }

    def run_parallel(self, category_urls):
        """并行爬取多个类别"""
        total_urls = len(category_urls)
        start_time = time.time()

        logger.info(f"Starting parallel scraping of {total_urls} URLs with {self.max_workers} workers")

        try:
            # 使用进程池并行处理
            with Pool(self.max_workers) as pool:
                # 使用tqdm显示进度
                results = list(tqdm(
                    pool.imap(self.scrape_category, category_urls),
                    total=total_urls,
                    desc="Scraping Progress"
                ))

            # 计算统计信息
            end_time = time.time()
            total_time = end_time - start_time
            successful = sum(1 for r in results if r['success'])

            # 打印详细的执行统计
            logger.info("\nParallel Scraping Statistics:")
            logger.info(f"Total Time: {total_time:.2f} seconds")
            logger.info(f"Average Time Per URL: {total_time / total_urls:.2f} seconds")
            logger.info(f"Success Rate: {successful}/{total_urls} ({successful / total_urls * 100:.1f}%)")

            # 打印文件保存信息
            logger.info("\nFile Processing Results:")
            for result in results:
                if result['success']:
                    logger.info(f"Category: {result['category_name']}")
                    logger.info(f"Initial file: {result['initial_file_path']}")
                    logger.info(f"Final file: {result['final_file_path']}")
                    logger.info("-" * 30)

            # 如果有失败的任务，打印详细信息
            failed_tasks = [r for r in results if not r['success']]
            if failed_tasks:
                logger.warning("\nFailed Tasks:")
                for task in failed_tasks:
                    logger.warning(f"URL: {task['url']}")
                    if 'error' in task:
                        logger.warning(f"Error: {task['error']}")
                    logger.warning("-" * 30)

            return results

        except Exception as e:
            logger.error(f"Error in parallel execution: {str(e)}")
            raise