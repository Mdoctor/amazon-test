from driver_manager import DriverManager
from scraper import AmazonScraper
from logger import logger


def main(headless=False):
    category_urls = [
        "https://www.amazon.com/Best-Sellers-Amazon-Devices-Accessories/zgbs/amazon-devices/ref=zg_bs_nav_amazon-devices_0",
        "https://www.amazon.com/Best-Sellers-Amazon-Renewed/zgbs/amazon-renewed/ref=zg_bs_nav_amazon-renewed_0",
        # "https://www.amazon.com/Best-Sellers-Appliances/zgbs/appliances/ref=zg_bs_nav_appliances_0",
        # "https://www.amazon.com/Best-Sellers-Apps-Games/zgbs/mobile-apps/ref=zg_bs_nav_mobile-apps_0",
        # "https://www.amazon.com/Best-Sellers-Arts-Crafts-Sewing/zgbs/arts-crafts/ref=zg_bs_nav_arts-crafts_0"
    ]

    driver_manager = None
    try:
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

    except Exception as e:
        logger.error(f"Main process error: {str(e)}")
    finally:
        if driver_manager:
            driver_manager.quit()


if __name__ == "__main__":
    main(headless=True)
