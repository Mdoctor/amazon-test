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

    def find_element_with_retry(self, selectors, max_retries=3):
        """使用多个选择器和重试机制查找元素"""
        for _ in range(max_retries):
            for by_method, selector in selectors:
                try:
                    element = self.wait.until(
                        EC.presence_of_element_located((getattr(By, by_method), selector))
                    )
                    if element and element.is_displayed():
                        return element
                except:
                    continue
            self.random_sleep(1, 2)
        return None

    def find_elements_with_retry(self, selectors, max_retries=3):
        """使用多个选择器和重试机制查找多个元素"""
        for _ in range(max_retries):
            for by_method, selector in selectors:
                try:
                    elements = self.driver.find_elements(getattr(By, by_method), selector)
                    if elements:
                        return elements
                except:
                    continue
            self.random_sleep(1, 2)
        return []

    def get_text_safely(self, element):
        """安全地获取元素文本"""
        if element:
            try:
                text = element.get_attribute('textContent') or element.text
                return text.strip()
            except:
                pass
        return 'N/A'

    def clean_price(self, price_text):
        """清理和标准化价格文本"""
        if price_text and price_text != 'N/A':
            try:
                # 尝试直接从价格文本中提取数字
                price_match = re.search(r'(\d+)\.?(\d*)', price_text)
                if price_match:
                    whole = price_match.group(1)
                    fraction = price_match.group(2) or '00'
                    return float(f"{whole}.{fraction}")

                # 如果上面失败，尝试分别查找整数和小数部分
                whole_elem = self.find_element_with_retry([
                    ('CSS_SELECTOR', '.a-price-whole'),
                    ('XPATH', "//span[contains(@class,'a-price-whole')]")
                ])
                fraction_elem = self.find_element_with_retry([
                    ('CSS_SELECTOR', '.a-price-fraction'),
                    ('XPATH', "//span[contains(@class,'a-price-fraction')]")
                ])

                if whole_elem:
                    whole = re.sub(r'[^\d]', '', self.get_text_safely(whole_elem))
                    fraction = re.sub(r'[^\d]', '', self.get_text_safely(fraction_elem)) if fraction_elem else '00'
                    return float(f"{whole}.{fraction}")

            except Exception as e:
                logger.warning(f"Error cleaning price: {str(e)}")
        return 'N/A'

    def _get_product_title(self):
        """获取商品标题"""
        title_elem = self.find_element_with_retry(ScraperConfig.TITLE_SELECTORS)
        return self.get_text_safely(title_elem)

    def _get_product_price(self):
        """获取商品价格"""
        price_elem = self.find_element_with_retry(ScraperConfig.PRICE_SELECTORS)
        price_text = self.get_text_safely(price_elem)
        return self.clean_price(price_text)

    def _get_product_rating(self):
        """获取商品评分"""
        try:
            # 尝试获取星级评分
            rating_script = self.driver.execute_script("""
                var ratingElement = document.querySelector('#acrPopover');
                if (ratingElement) {
                    return ratingElement.getAttribute('title');
                }
                return null;
            """)

            if rating_script:
                rating_match = re.search(r'(\d+\.?\d*)\s+out of\s+5', rating_script)
                if rating_match:
                    return rating_match.group(1)

            # 备选方法：尝试其他选择器
            selectors = [
                ('CSS_SELECTOR', '#acrPopover'),
                ('CSS_SELECTOR', 'span[data-hook="rating-out-of-text"]'),
                ('CSS_SELECTOR', '.a-icon-star .a-icon-alt'),
                ('XPATH', '//span[@class="a-icon-alt"]')
            ]

            for by_method, selector in selectors:
                element = self.safe_find_element(getattr(By, by_method), selector)
                if element:
                    text = element.get_attribute('title') or element.text
                    if text:
                        rating_match = re.search(r'(\d+\.?\d*)\s+out of\s+5', text)
                        if rating_match:
                            return rating_match.group(1)

        except Exception as e:
            logger.warning(f"Error getting rating: {str(e)}")

        return 'N/A'

    def _get_review_count(self):
        """获取评论数量"""
        try:
            # 使用JavaScript获取评论数
            review_count = self.driver.execute_script("""
                var reviewElement = document.querySelector('#acrCustomerReviewText');
                if (reviewElement) {
                    return reviewElement.textContent;
                }
                var altElement = document.querySelector('#reviews-medley-footer .a-size-base');
                if (altElement) {
                    return altElement.textContent;
                }
                return null;
            """)

            if review_count:
                # 提取数字
                count_match = re.search(r'([\d,]+)', review_count)
                if count_match:
                    return count_match.group(1).replace(',', '')

            # 备选方法：尝试其他选择器
            selectors = [
                ('CSS_SELECTOR', '#acrCustomerReviewText'),
                ('CSS_SELECTOR', '#reviews-medley-footer .a-size-base'),
                ('XPATH', '//span[@id="acrCustomerReviewText"]'),
                ('CSS_SELECTOR', 'a[data-hook="see-all-reviews-link-foot"]')
            ]

            for by_method, selector in selectors:
                element = self.safe_find_element(getattr(By, by_method), selector)
                if element:
                    text = element.text
                    if text:
                        count_match = re.search(r'([\d,]+)', text)
                        if count_match:
                            return count_match.group(1).replace(',', '')

        except Exception as e:
            logger.warning(f"Error getting review count: {str(e)}")

        return 'N/A'

    def _get_product_description(self):
        """获取商品描述"""
        desc_elem = self.find_element_with_retry(ScraperConfig.DESCRIPTION_SELECTORS)
        description = self.get_text_safely(desc_elem)
        return description[:1000] if description != 'N/A' else 'N/A'

    def _get_product_image(self):
        """获取商品主图"""
        image_elem = self.find_element_with_retry(ScraperConfig.IMAGE_SELECTORS)
        if image_elem:
            try:
                return image_elem.get_attribute('src')
            except:
                pass
        return 'N/A'

    def _get_product_brand(self):
        """获取商品品牌"""
        try:
            brand_elem = self.find_element_with_retry(ScraperConfig.BRAND_SELECTORS)
            if brand_elem:
                brand_text = self.get_text_safely(brand_elem)
                if brand_text and brand_text != 'N/A':
                    # 改进品牌文本清理逻辑
                    brand_text = brand_text.replace('Brand:', '').replace('Visit the', '').replace('Store', '')

                    # 移除首尾的符号和空格
                    brand_text = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', brand_text)

                    # 移除多余的空格和重复的词
                    words = [word.strip() for word in brand_text.split() if word.strip()]
                    # 移除每个词首尾的符号
                    words = [re.sub(r'^[^\w]+|[^\w]+$', '', word) for word in words]

                    # 移除重复的词并过滤掉空字符串
                    unique_words = []
                    for word in words:
                        if word and word not in unique_words:
                            unique_words.append(word)

                    brand_text = ' '.join(unique_words).strip()
                    if brand_text:
                        return brand_text

                # 如果上面的方法失败，尝试获取href属性中的品牌信息
                brand_url = brand_elem.get_attribute('href')
                if brand_url:
                    brand_match = re.search(r'/stores/([^/]+)/', brand_url)
                    if brand_match:
                        brand_name = brand_match.group(1).replace('-', ' ').title()
                        # 同样处理可能的重复和符号
                        words = [word.strip() for word in brand_name.split() if word.strip()]
                        words = [re.sub(r'^[^\w]+|[^\w]+$', '', word) for word in words]
                        unique_words = []
                        for word in words:
                            if word and word not in unique_words:
                                unique_words.append(word)
                        brand_name = ' '.join(unique_words).strip()
                        if brand_name:
                            return brand_name

            # 尝试从页面标题中提取品牌
            title = self._get_product_title()
            if title != 'N/A':
                first_word = title.split()[0]
                # 清理首个词的首尾符号
                first_word = re.sub(r'^[^\w]+|[^\w]+$', '', first_word)
                if len(first_word) > 2:  # 避免像"A"、"An"这样的词
                    return first_word.strip()

        except Exception as e:
            logger.warning(f"Error getting brand: {str(e)}")

        return 'N/A'

    def _get_product_availability(self):
        """获取商品可用性状态"""
        try:
            # 使用JavaScript获取库存状态
            availability = self.driver.execute_script("""
                var availabilityElement = document.querySelector('#availability span');
                if (availabilityElement) {
                    return availabilityElement.textContent.trim();
                }
                var merchantElement = document.querySelector('#merchantInfoFeature');
                if (merchantElement) {
                    return merchantElement.textContent.trim();
                }
                var buyboxElement = document.querySelector('#buybox-see-all-buying-choices');
                if (buyboxElement) {
                    return buyboxElement.textContent.trim();
                }
                return null;
            """)

            if availability:
                return availability.strip()

            # 备选方法：尝试其他选择器
            selectors = [
                ('CSS_SELECTOR', '#availability span'),
                ('CSS_SELECTOR', '#merchantInfoFeature'),
                ('CSS_SELECTOR', '#buybox-see-all-buying-choices'),
                ('XPATH', '//div[@id="availability"]//span[@class="a-size-medium a-color-success"]'),
                ('CSS_SELECTOR', '#outOfStock .a-color-price')
            ]

            for by_method, selector in selectors:
                element = self.safe_find_element(getattr(By, by_method), selector)
                if element:
                    text = element.text.strip()
                    if text:
                        return text

            # 检查是否缺货
            out_of_stock = self.safe_find_element(By.CSS_SELECTOR, '#outOfStock')
            if out_of_stock:
                return "Currently unavailable"

        except Exception as e:
            logger.warning(f"Error getting availability: {str(e)}")

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

                logger.info(f"Attempting to navigate to URL: {url}")
                self.driver.get(url)
                logger.info("Successfully navigated to URL")  # 添加这行

                self.random_sleep()

                if self._check_and_handle_throttling():
                    logger.info("Throttling detected, will retry...")
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
            if not self._handle_page_with_retry(url):
                return None

            # 等待页面主要内容加载
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # 添加短暂滚动以触发动态内容加载
            self.driver.execute_script("window.scrollTo(0, 200)")
            self.random_sleep(1, 2)

            # 确保价格元素已加载
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.a-price'))
            )

            product_info = {
                'url': url,
                'asin': self._extract_asin(url),
                'title': self._get_product_title(),
                'price': self._get_product_price(),
                'rating': self._get_product_rating(),
                'review_count': self._get_review_count(),
                'description': self._get_product_description(),
                'image_url': self._get_product_image(),
                'brand': self._get_product_brand(),
                'availability': self._get_product_availability(),
                'category': self.category_name,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }

            # 验证关键字段
            if product_info['title'] == 'N/A' and product_info['price'] == 'N/A':
                logger.warning(f"Failed to extract essential information for {url}")
                return None

            return product_info

        except Exception as e:
            logger.error(f"Error extracting product info from {url}: {str(e)}")
            return None

    def _get_category_name(self, category_url):
        """获取类别名称"""
        # 首先尝试从URL中提取类别名称
        if category_url:
            # 匹配 Best-Sellers- 后面的部分，直到下一个斜杠
            match = re.search(r'Best-Sellers-(.*?)/zgbs', category_url)
            if match:
                category_name = match.group(1)
                # 解码URL编码的字符
                category_name = unquote(category_name)
                # 如果类别名称包含多个连字符分隔的词，保持原样
                return category_name

        # 如果从URL无法获取，尝试从页面元素获取
        for selector in ScraperConfig.CATEGORY_NAME_SELECTORS:
            try:
                category_elem = self.safe_find_element(By.XPATH, selector)
                if category_elem:
                    return category_elem.text.strip()
            except:
                continue

        # 如果都失败了，返回默认值
        return "Amazon_Bestsellers"

    def get_bestsellers(self, category_url=None):
        """获取畅销商品列表"""
        try:
            url = category_url or "https://www.amazon.com/Best-Sellers/zgbs/"
            if not self._handle_page_with_retry(url):
                return []

            # 执行页面滚动
            self.scroll_page()

            # 获取类别名称
            self.category_name = self._get_category_name(category_url)

            # 使用JavaScript获取所有产品链接
            product_links = set()
            for selector in ScraperConfig.PRODUCT_LINK_SELECTORS:
                try:
                    links = self.driver.execute_script(f"""
                        return Array.from(document.querySelectorAll("{selector}"))
                            .filter(el => el.href && el.href.includes('/dp/'))
                            .map(el => {{
                                let match = el.href.match(/\/dp\/([A-Z0-9]{{10}})/);
                                return match ? 'https://www.amazon.com/dp/' + match[1] : null;
                            }})
                            .filter(url => url);
                    """)
                    product_links.update(links)

                    if len(product_links) >= ScraperConfig.MAX_PRODUCTS_PER_CATEGORY:
                        break
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {str(e)}")
                    continue

            unique_links = list(product_links)[:ScraperConfig.MAX_PRODUCTS_PER_CATEGORY]
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