from parallel_scraper import ParallelScraper
from logger import logger
import sys
from config import ScraperConfig
from urllib.parse import quote_plus
import time


def main():
    try:
        # 搜索关键词列表
        search_terms = [
            "shoes for men",
            "apple",
            # "laptop",
            # "headphones",
            # "gaming mouse"
        ]

        logger.info(f"Starting parallel scraping for {len(search_terms)} search terms")
        start_time = time.time()

        # 构建搜索URL，添加排序参数以获取最相关的结果
        search_urls = [
            f"https://www.amazon.com/s?k={quote_plus(term)}&s=exact-aware-popularity-rank&ref=nb_sb_noss"
            for term in search_terms
        ]

        # 创建并行爬虫实例，设置合理的worker数量
        max_workers = min(len(search_terms), ScraperConfig.MAX_WORKERS)
        parallel_scraper = ParallelScraper(max_workers)

        # 运行并行爬虫
        results = parallel_scraper.run_parallel(search_urls)

        # 统计结果
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful

        # 计算总耗时
        total_time = time.time() - start_time

        # 打印详细的执行报告
        logger.info("\n" + "=" * 50)
        logger.info("Execution Summary:")
        logger.info("=" * 50)
        logger.info(f"Total Search Terms: {len(search_terms)}")
        logger.info(f"Successfully Scraped: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Total Execution Time: {total_time:.2f} seconds")
        logger.info(f"Average Time Per Term: {total_time/len(search_terms):.2f} seconds")
        logger.info("=" * 50)

        # 打印每个搜索词的结果
        logger.info("\nDetailed Results:")
        for term, result in zip(search_terms, results):
            status = "✓ Success" if result['success'] else "✗ Failed"
            logger.info(f"Search Term: {term}")
            logger.info(f"Status: {status}")
            logger.info(f"Category Name: {result.get('category_name', 'N/A')}")
            logger.info("-" * 30)

    except Exception as e:
        logger.error(f"Main process error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()