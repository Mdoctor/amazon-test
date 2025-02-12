from parallel_scraper import ParallelScraper
from logger import logger
import sys


def main():
    try:
        category_urls = [
            "https://www.amazon.com/Best-Sellers-Amazon-Devices-Accessories/zgbs/amazon-devices/ref=zg_bs_nav_amazon-devices_0",
            "https://www.amazon.com/Best-Sellers-Amazon-Renewed/zgbs/amazon-renewed/ref=zg_bs_nav_amazon-renewed_0",
            # "https://www.amazon.com/Best-Sellers-Appliances/zgbs/appliances/ref=zg_bs_nav_appliances_0",
            # "https://www.amazon.com/Best-Sellers-Apps-Games/zgbs/mobile-apps/ref=zg_bs_nav_mobile-apps_0",
            # "https://www.amazon.com/Best-Sellers-Arts-Crafts-Sewing/zgbs/arts-crafts/ref=zg_bs_nav_arts-crafts_0"
        ]

        # 创建并行爬虫实例（使用默认CPU核心数或指定数量）
        parallel_scraper = ParallelScraper(max_workers=4)  # 可以根据需要调整worker数量

        # 运行并行爬虫
        results = parallel_scraper.run_parallel(category_urls)

        # 统计结果
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful

        logger.info(f"\nFinal Statistics:")
        logger.info(f"Total Categories: {len(results)}")
        logger.info(f"Successfully Scraped: {successful}")
        logger.info(f"Failed: {failed}")

    except Exception as e:
        logger.error(f"Main process error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()