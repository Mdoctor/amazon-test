from driver_manager import DriverManager
from scraper import AmazonScraper
from logger import logger
import time
import sys


def main(headless=False, max_retries=3):
    driver_manager = None
    retry_count = 0

    while retry_count < max_retries:
        try:
            category_urls = [
                "https://www.amazon.com/Best-Sellers-Amazon-Devices-Accessories/zgbs/amazon-devices/ref=zg_bs_nav_amazon-devices_0",
                # "https://www.amazon.com/Best-Sellers-Amazon-Renewed/zgbs/amazon-renewed/ref=zg_bs_nav_amazon-renewed_0",
                # "https://www.amazon.com/Best-Sellers-Appliances/zgbs/appliances/ref=zg_bs_nav_appliances_0",
                # "https://www.amazon.com/Best-Sellers-Apps-Games/zgbs/mobile-apps/ref=zg_bs_nav_mobile-apps_0",
                # "https://www.amazon.com/Best-Sellers-Arts-Crafts-Sewing/zgbs/arts-crafts/ref=zg_bs_nav_arts-crafts_0"
            ]

            driver_manager = DriverManager()
            driver_manager.setup_driver(headless=headless)

            scraper = AmazonScraper(driver_manager)
            results = scraper.run_multiple_categories(category_urls)

            # 统计结果
            successful = sum(1 for r in results if r['success'])
            failed = len(results) - successful

            logger.info(f"\nFinal Statistics:")
            logger.info(f"Total Categories: {len(results)}")
            logger.info(f"Successfully Scraped: {successful}")
            logger.info(f"Failed: {failed}")

            break

        except Exception as e:
            retry_count += 1
            logger.error(f"Main process error (Attempt {retry_count}/{max_retries}): {str(e)}")

            if driver_manager:
                driver_manager.quit()
                driver_manager = None

            if retry_count < max_retries:
                sleep_time = (2 ** retry_count) + (retry_count * 2)
                logger.info(f"Waiting {sleep_time} seconds before retrying...")
                time.sleep(sleep_time)
            else:
                logger.error("Maximum retry attempts reached. Exiting...")
                sys.exit(1)

        finally:
            if driver_manager:
                driver_manager.quit()


if __name__ == "__main__":
    main(headless=True)
