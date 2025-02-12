import os

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
from fake_useragent import UserAgent
import logging
import pandas as pd
import re
from urllib.parse import unquote

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)


class AmazonScraper:
    # 类级别的配置
    WAIT_TIME = 10
    MIN_SLEEP = 2
    MAX_SLEEP = 5
    SCROLL_STEPS = 3

    def __init__(self):
        self.driver = None
        self.wait = None
        self.products = []
        self.category_name = None
        self.setup_driver()

    def __del__(self):
        """析构函数，安全地关闭驱动"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logging.warning(f"Error in driver cleanup: {str(e)}")

    def setup_driver(self):
        """配置并初始化Chrome驱动"""
        try:
            options = uc.ChromeOptions()

            # 基本设置
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--start-maximized')
            options.add_argument('--window-size=1920,1080')  # 添加固定窗口大小

            # 添加反检测参数
            options.add_argument('--disable-blink-features=AutomationControlled')

            # 随机User-Agent
            ua = UserAgent()
            options.add_argument(f'--user-agent={ua.random}')

            # 初始化驱动
            self.driver = uc.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, self.WAIT_TIME)

            # 执行反检测JavaScript
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            """)

            logging.info("Chrome driver setup successful")

        except Exception as e:
            logging.error(f"Failed to setup Chrome driver: {str(e)}")
            raise

    def scroll_page(self):
        """滚动页面以加载更多内容"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")

            for _ in range(self.SCROLL_STEPS):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.random_sleep(1, 2)  # 较短的等待时间

                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

        except Exception as e:
            logging.warning(f"Error during page scroll: {str(e)}")

    def random_sleep(self, min_time=None, max_time=None):
        """随机等待时间"""
        min_time = min_time or self.MIN_SLEEP
        max_time = max_time or self.MAX_SLEEP
        sleep_time = random.uniform(min_time, max_time)
        logging.debug(f"Sleeping for {sleep_time:.2f} seconds")
        time.sleep(sleep_time)

    def safe_find_element(self, by, value, wait=True):
        """安全地查找元素，带有等待和错误处理"""
        try:
            if wait:
                element = self.wait.until(EC.presence_of_element_located((by, value)))
                return element
            return self.driver.find_element(by, value)
        except (TimeoutException, NoSuchElementException) as e:
            logging.debug(f"Element not found: {value} - {str(e)}")
            return None
        except Exception as e:
            logging.warning(f"Error finding element {value}: {str(e)}")
            return None

    def extract_product_info(self, url):
        """提取商品详细信息"""
        try:
            self.driver.get(url)
            self.random_sleep()

            product_info = {}

            # 1. 提取标题
            title_selectors = [
                (By.ID, "productTitle"),
                (By.CSS_SELECTOR, "h1.a-text-normal"),
                (By.CSS_SELECTOR, "span#productTitle")
            ]
            for by, selector in title_selectors:
                title_elem = self.safe_find_element(by, selector)
                if title_elem and title_elem.text.strip():
                    product_info['title'] = title_elem.text.strip()
                    break
            if 'title' not in product_info:
                product_info['title'] = 'N/A'

            # 2. 提取价格
            price_selectors = [
                (By.CSS_SELECTOR, "span.a-price-whole"),
                (By.ID, "priceblock_ourprice"),
                (By.ID, "priceblock_dealprice"),
                (By.CSS_SELECTOR, "span.a-offscreen")
            ]
            product_info['price'] = 'N/A'
            for by, selector in price_selectors:
                price_elem = self.safe_find_element(by, selector)
                if price_elem and price_elem.text.strip():
                    product_info['price'] = price_elem.text.strip()
                    break

            # 3. 提取评分
            rating_selectors = [
                (By.CSS_SELECTOR, "span.a-icon-alt"),
                (By.CSS_SELECTOR, "i.a-icon-star span.a-icon-alt"),
                (By.CSS_SELECTOR, "#acrPopover span.a-icon-alt")
            ]
            product_info['rating'] = 'N/A'
            for by, selector in rating_selectors:
                rating_elem = self.safe_find_element(by, selector)
                if rating_elem and rating_elem.text.strip():
                    rating_text = rating_elem.text.strip()
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        product_info['rating'] = rating_match.group(1)
                        break

            # 4. 提取评论数量
            review_count_selectors = [
                (By.ID, "acrCustomerReviewText"),
                (By.CSS_SELECTOR, "span#acrCustomerReviewText"),
                (By.CSS_SELECTOR, "[data-csa-c-func-deps='acrCustomerReviewText']")
            ]
            product_info['review_count'] = 'N/A'
            for by, selector in review_count_selectors:
                review_elem = self.safe_find_element(by, selector)
                if review_elem and review_elem.text.strip():
                    count_text = review_elem.text.strip()
                    count_match = re.search(r'([\d,]+)', count_text)
                    if count_match:
                        product_info['review_count'] = count_match.group(1)
                        break

            # 5. 提取ASIN
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
            product_info['asin'] = asin_match.group(1) if asin_match else 'N/A'

            # 6. 提取商品描述（如果有）
            description_selectors = [
                (By.ID, "productDescription"),
                (By.CSS_SELECTOR, "#feature-bullets .a-list-item"),
                (By.CSS_SELECTOR, "#feature-bullets")
            ]
            product_info['description'] = 'N/A'
            for by, selector in description_selectors:
                desc_elem = self.safe_find_element(by, selector)
                if desc_elem and desc_elem.text.strip():
                    product_info['description'] = desc_elem.text.strip()[:500]  # 限制描述长度
                    break

            return product_info

        except Exception as e:
            logging.error(f"Error extracting product info from {url}: {str(e)}")
            return None

    def get_bestsellers(self, category_url=None):
        """获取畅销商品列表"""
        try:
            url = category_url or "https://www.amazon.com/Best-Sellers/zgbs/"
            self.driver.get(url)
            self.random_sleep()

            # 滚动页面以确保加载所有内容
            self.scroll_page()

            # 获取类别名称
            category_name_selectors = [
                "//span[@class='category-title']",
                "//h1[contains(@class, 'category-title')]",
                "//div[contains(@class, 'category-title')]",
                "//h1[contains(@class, 'a-size-large')]"  # 添加新的选择器
            ]

            self.category_name = None
            for selector in category_name_selectors:
                try:
                    category_elem = self.safe_find_element(By.XPATH, selector)
                    if category_elem:
                        self.category_name = category_elem.text.strip()
                        break
                except:
                    continue

            if not self.category_name:
                match = re.search(r'Best-Sellers-([^/]+)', category_url)
                if match:
                    self.category_name = unquote(match.group(1)).replace('-', ' ')
                else:
                    self.category_name = "Amazon_Bestsellers"

            product_links = []
            selectors = [
                "a[href*='/dp/']",  # 更通用的选择器
                ".zg-item-immersion a[href*='/dp/']",
                ".zg-grid-general-faceout a[href*='/dp/']",
                "div[data-component-type='s-search-result'] a[href*='/dp/']",
                ".a-link-normal[href*='/dp/']"
            ]

            for selector in selectors:
                try:
                    # 使用JavaScript获取元素
                    elements = self.driver.execute_script(f"""
                        return Array.from(document.querySelectorAll("{selector}"))
                            .filter(el => el.href && el.href.includes('/dp/'));
                    """)

                    for element in elements:
                        href = element.get_attribute('href')
                        if href and '/dp/' in href:
                            # 提取ASIN
                            asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
                            if asin_match:
                                base_url = f"https://www.amazon.com/dp/{asin_match.group(1)}"
                                if base_url not in product_links:
                                    product_links.append(base_url)

                    if len(product_links) >= 10:
                        break

                except Exception as e:
                    logging.debug(f"Selector {selector} failed: {str(e)}")
                    continue

            unique_links = list(dict.fromkeys(product_links))[:10]
            logging.info(f"Found {len(unique_links)} unique product links")
            return unique_links

        except Exception as e:
            logging.error(f"Error getting bestsellers: {str(e)}")
            return []

    def save_to_excel(self):
        """保存商品信息到Excel文件"""
        try:
            if not self.products:
                logging.warning("No products to save")
                return

            # 确保类别名称适合作为文件名
            safe_category_name = re.sub(r'[<>:"/\\|?*]', '_', self.category_name)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f'{safe_category_name}_bestsellers_{timestamp}.xlsx'

            # 创建DataFrame
            df = pd.DataFrame([
                {
                    'Rank': i + 1,
                    'Title': p['title'],
                    'Price': p['price'],
                    'Rating': p['rating'],
                    'Review Count': p['review_count'],
                    'ASIN': p['asin'],
                    'Description': p['description']
                }
                for i, p in enumerate(self.products)
            ])

            # 尝试多个可能的目录来保存文件
            possible_dirs = [
                '.',  # 当前目录
                os.path.expanduser('~'),  # 用户主目录
                os.path.join(os.path.expanduser('~'), 'Documents'),  # 文档目录
                os.getenv('TEMP', os.path.expanduser('~'))  # 临时目录
            ]

            for save_dir in possible_dirs:
                try:
                    full_path = os.path.join(save_dir, filename)
                    # 使用ExcelWriter以便于设置格式
                    with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Bestsellers')

                        # 自动调整列宽
                        worksheet = writer.sheets['Bestsellers']
                        for idx, col in enumerate(df.columns):
                            max_length = max(
                                df[col].astype(str).apply(len).max(),
                                len(col)
                            )
                            # 限制最大列宽
                            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)

                    logging.info(f"Successfully saved {len(self.products)} products to {full_path}")
                    return  # 如果成功保存，就退出函数

                except PermissionError:
                    logging.warning(f"Permission denied when trying to save to {save_dir}, trying next location...")
                    continue
                except Exception as e:
                    logging.warning(f"Error saving to {save_dir}: {str(e)}, trying next location...")
                    continue

            # 如果所有尝试都失败了
            raise Exception("Unable to save file in any of the attempted locations")

        except Exception as e:
            logging.error(f"Error saving to Excel: {str(e)}")
            # 尝试将数据保存为CSV作为后备选项
            try:
                csv_filename = f'{safe_category_name}_bestsellers_{timestamp}.csv'
                csv_path = os.path.join(os.getenv('TEMP', '.'), csv_filename)
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                logging.info(f"Saved data as CSV instead at: {csv_path}")
            except Exception as csv_error:
                logging.error(f"Failed to save as CSV as well: {str(csv_error)}")

    def run(self, category_url=None):
        """运行爬虫"""
        try:
            product_links = self.get_bestsellers(category_url)

            for i, link in enumerate(product_links, 1):
                logging.info(f"Scraping product {i}/{len(product_links)}: {link}")

                product = self.extract_product_info(link)  # 使用新的extract_product_info方法
                if product:
                    self.products.append(product)

                if i < len(product_links):
                    self.random_sleep(3, 7)

            # 保存数据到Excel
            self.save_to_excel()

        except Exception as e:
            logging.error(f"Error in main scraping process: {str(e)}")

        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    self.driver = None
                    logging.info("Chrome driver closed successfully")
                except Exception as e:
                    logging.error(f"Error closing Chrome driver: {str(e)}")


def main():
    try:
        # 可以指定特定类别的URL
        category_url = "https://www.amazon.com/Best-Sellers-Amazon-Devices-Accessories/zgbs/amazon-devices/ref=zg_bs_nav_amazon-devices_0"
        scraper = AmazonScraper()
        scraper.run(category_url)
    except Exception as e:
        logging.error(f"Main process error: {str(e)}")


if __name__ == "__main__":
    main()