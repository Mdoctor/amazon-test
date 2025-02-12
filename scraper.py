import re
import time
import random
from urllib.parse import unquote
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import ScraperConfig
from logger import logger
from data_saver import DataSaver


class AmazonScraper:
    def __init__(self, driver_manager):
        self.driver_manager = driver_manager
        self.driver = driver_manager.driver
        self.wait = driver_manager.wait
        self.products = []
        self.category_name = None

    def scroll_page(self):
        """滚动页面以加载更多内容"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            for _ in range(ScraperConfig.SCROLL_STEPS):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.random_sleep(1, 2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        except Exception as e:
            logger.warning(f"Error during page scroll: {str(e)}")

    def random_sleep(self, min_time=None, max_time=None):
        """随机等待时间"""
        min_time = min_time or ScraperConfig.MIN_SLEEP
        max_time = max_time or ScraperConfig.MAX_SLEEP
        sleep_time = random.uniform(min_time, max_time)
        time.sleep(sleep_time)

    def safe_find_element(self, by, value, wait=True):
        """安全地查找元素"""
        try:
            if wait:
                return self.wait.until(EC.presence_of_element_located((by, value)))
            return self.driver.find_element(by, value)
        except (TimeoutException, NoSuchElementException) as e:
            logger.debug(f"Element not found: {value} - {str(e)}")
            return None
        except Exception as e:
            logger.warning(f"Error finding element {value}: {str(e)}")
            return None

    def _get_product_title(self):
        """获取商品标题"""
        for by_method, selector in ScraperConfig.TITLE_SELECTORS:
            title_elem = self.safe_find_element(getattr(By, by_method), selector)
            if title_elem and title_elem.text.strip():
                return title_elem.text.strip()
        return 'N/A'

    def _get_product_price(self):
        """获取商品价格"""
        for by_method, selector in ScraperConfig.PRICE_SELECTORS:
            price_elem = self.safe_find_element(getattr(By, by_method), selector)
            if price_elem and price_elem.text.strip():
                return price_elem.text.strip()
        return 'N/A'

    def _get_product_rating(self):
        """获取商品评分"""
        for by_method, selector in ScraperConfig.RATING_SELECTORS:
            rating_elem = self.safe_find_element(getattr(By, by_method), selector)
            if rating_elem and rating_elem.text.strip():
                rating_text = rating_elem.text.strip()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    return rating_match.group(1)
        return 'N/A'

    def _get_review_count(self):
        """获取评论数量"""
        for by_method, selector in ScraperConfig.REVIEW_COUNT_SELECTORS:
            review_elem = self.safe_find_element(getattr(By, by_method), selector)
            if review_elem and review_elem.text.strip():
                count_text = review_elem.text.strip()
                count_match = re.search(r'([\d,]+)', count_text)
                if count_match:
                    return count_match.group(1)
        return 'N/A'

    def _get_product_description(self):
        """获取商品描述"""
        for by_method, selector in ScraperConfig.DESCRIPTION_SELECTORS:
            desc_elem = self.safe_find_element(getattr(By, by_method), selector)
            if desc_elem and desc_elem.text.strip():
                return desc_elem.text.strip()[:500]  # 限制描述长度
        return 'N/A'

    def _extract_asin(self, url):
        """从URL中提取ASIN"""
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
        return asin_match.group(1) if asin_match else 'N/A'

    def _check_and_handle_throttling(self):
        """检查是否出现限流信息并处理"""
        try:
            throttle_text = "Request was throttled. Please wait a moment and refresh the page"
            page_source = self.driver.page_source
            if throttle_text in page_source:
                logger.warning("Detected throttling message, attempting to refresh...")
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking throttling: {str(e)}")
            return False

    def _handle_page_with_retry(self, url, max_retries=10):
        """处理页面加载，包含重试逻辑"""
        retries = 0
        while retries < max_retries:
            try:
                if retries > 0:
                    logger.info(f"Retry attempt {retries}/{max_retries}")

                logger.info(f"Attempting to navigate to URL: {url}")  # 添加这行
                self.driver.get(url)
                logger.info("Successfully navigated to URL")  # 添加这行

                self.random_sleep()

                if self._check_and_handle_throttling():
                    logger.info("Throttling detected, will retry...")  # 添加这行
                    retries += 1
                    self.random_sleep(3, 5)
                    continue

                return True  # 页面加载成功且无限流信息

            except Exception as e:
                logger.error(f"Error loading page (attempt {retries + 1}/{max_retries}): {str(e)}")
                retries += 1
                if retries < max_retries:
                    self.random_sleep(3, 5)

        logger.error(f"Failed to load page after {max_retries} attempts: {url}")
        return False

    def extract_product_info(self, url):
        """提取商品详细信息"""
        try:
            # 使用新的重试逻辑加载页面
            if not self._handle_page_with_retry(url):
                return None

            product_info = {
                'title': self._get_product_title(),
                'price': self._get_product_price(),
                'rating': self._get_product_rating(),
                'review_count': self._get_review_count(),
                'description': self._get_product_description(),
                'asin': self._extract_asin(url)
            }

            return product_info

        except Exception as e:
            logger.error(f"Error extracting product info from {url}: {str(e)}")
            return None

    def _get_category_name(self, category_url):
        """获取类别名称"""
        for selector in ScraperConfig.CATEGORY_NAME_SELECTORS:
            try:
                category_elem = self.safe_find_element(By.XPATH, selector)
                if category_elem:
                    return category_elem.text.strip()
            except:
                continue

        # 如果无法从页面获取类别名称，尝试从URL提取
        match = re.search(r'Best-Sellers-([^/]+)', category_url)
        if match:
            return unquote(match.group(1)).replace('-', ' ')
        return "Amazon_Bestsellers"

    def get_bestsellers(self, category_url=None):
        """获取畅销商品列表"""
        try:
            url = category_url or "https://www.amazon.com/Best-Sellers/zgbs/"

            # 使用新的重试逻辑加载页面
            if not self._handle_page_with_retry(url):
                return []

            self.scroll_page()

            # 获取类别名称
            self.category_name = self._get_category_name(category_url)

            product_links = []
            for selector in ScraperConfig.PRODUCT_LINK_SELECTORS:
                try:
                    elements = self.driver.execute_script(f"""
                        return Array.from(document.querySelectorAll("{selector}"))
                            .filter(el => el.href && el.href.includes('/dp/'));
                    """)

                    for element in elements:
                        href = element.get_attribute('href')
                        if href and '/dp/' in href:
                            asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
                            if asin_match:
                                base_url = f"https://www.amazon.com/dp/{asin_match.group(1)}"
                                if base_url not in product_links:
                                    product_links.append(base_url)

                    if len(product_links) >= 10:
                        break

                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {str(e)}")
                    continue

            unique_links = list(dict.fromkeys(product_links))[:10]
            logger.info(f"Found {len(unique_links)} unique product links")
            return unique_links

        except Exception as e:
            logger.error(f"Error getting bestsellers: {str(e)}")
            return []

    def run(self, category_url=None):
        """运行爬虫"""
        try:
            self.products = []
            product_links = self.get_bestsellers(category_url)

            for i, link in enumerate(product_links, 1):
                logger.info(f"Scraping product {i}/{len(product_links)}: {link}")
                product = self.extract_product_info(link)
                if product:
                    self.products.append(product)
                if i < len(product_links):
                    self.random_sleep(3, 7)

            # 保存数据到Excel
            DataSaver.save_to_excel(self.products, self.category_name)
            return True

        except Exception as e:
            logger.error(f"Error in main scraping process: {str(e)}")
            return False

    def run_multiple_categories(self, category_urls):
        """运行多个类别的爬虫"""
        results = []
        total_categories = len(category_urls)

        for i, url in enumerate(category_urls, 1):
            try:
                logger.info(f"\n{'=' * 50}")
                logger.info(f"Processing category {i}/{total_categories}: {url}")
                logger.info('=' * 50)

                success = self.run(url)
                results.append({
                    'url': url,
                    'success': success,
                    'category_name': self.category_name
                })

                if i < total_categories:
                    self.random_sleep(5, 10)

            except Exception as e:
                logger.error(f"Error processing category {url}: {str(e)}")
                results.append({
                    'url': url,
                    'success': False,
                    'category_name': None
                })

        # 打印汇总报告
        self._print_summary_report(results)
        return results

    def _print_summary_report(self, results):
        """打印爬取结果汇总报告"""
        logger.info("\n" + "=" * 50)
        logger.info("Scraping Summary Report")
        logger.info("=" * 50)
        for result in results:
            status = "Success" if result['success'] else "Failed"
            logger.info(f"Category: {result['category_name'] or 'Unknown'}")
            logger.info(f"URL: {result['url']}")
            logger.info(f"Status: {status}")
            logger.info("-" * 50)