import re
import time
import random
from urllib.parse import unquote
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

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

    def safe_find_element(self, by, selector, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            logger.warning(f"Timeout waiting for element: {selector}")
            return None
        except Exception as e:
            logger.error(f"Error finding element {selector}: {str(e)}")
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
        try:
            # 首先尝试获取apexPriceToPay中的价格
            price_script = self.driver.execute_script("""
                let priceElement = document.querySelector('.apexPriceToPay .a-offscreen');
                if (priceElement) {
                    return priceElement.textContent;
                }
                // 如果找不到主价格，尝试其他价格元素
                let alternativePriceElements = [
                    '.a-price .a-offscreen',
                    '#priceblock_ourprice',
                    '#priceblock_dealprice',
                    '.a-price.a-text-price span[aria-hidden="true"]'
                ];
                for (let selector of alternativePriceElements) {
                    let element = document.querySelector(selector);
                    if (element) {
                        return element.textContent;
                    }
                }
                return null;
            """)

            if price_script:
                # 移除货币符号和其他非数字字符
                price_text = price_script.replace('$', '').replace(',', '').strip()
                price_match = re.search(r'(\d+\.?\d*)', price_text)
                if price_match:
                    price = float(price_match.group(1))
                    return "{:.2f}".format(price)

            # 如果JavaScript方法失败，尝试直接的DOM查询
            price_selectors = [
                ('CSS_SELECTOR', '.apexPriceToPay .a-offscreen'),
                ('CSS_SELECTOR', '.a-price .a-offscreen'),
                ('CSS_SELECTOR', '.a-price.a-text-price span[aria-hidden="true"]'),
                ('ID', 'priceblock_ourprice'),
                ('ID', 'priceblock_dealprice')
            ]

            for by_method, selector in price_selectors:
                price_elem = self.safe_find_element(getattr(By, by_method), selector)
                if price_elem:
                    price_text = price_elem.get_attribute('textContent')
                    if price_text:
                        price_text = price_text.replace('$', '').replace(',', '').strip()
                        price_match = re.search(r'(\d+\.?\d*)', price_text)
                        if price_match:
                            price = float(price_match.group(1))
                            return "{:.2f}".format(price)

        except Exception as e:
            logger.warning(f"Error cleaning price: {str(e)}")

        return 'N/A'

    def _get_product_title(self):
        """获取商品标题"""
        title_elem = self.find_element_with_retry(ScraperConfig.TITLE_SELECTORS)
        return self.get_text_safely(title_elem)

    def _get_product_price(self):
        """获取商品价格"""
        try:
            # 方案1: 检查第一种价格类型 (带有 apexPriceToPay 的表格形式)
            price_script = """
                let apexPrice = document.querySelector('.apexPriceToPay .a-offscreen');
                if (apexPrice) {
                    return apexPrice.textContent.trim();
                }
                return null;
            """
            apex_price = self.driver.execute_script(price_script)
            if apex_price:
                price_match = re.search(r'\$?([\d,]+\.?\d*)', apex_price)
                if price_match:
                    return float(price_match.group(1).replace(',', ''))

            # 方案2: 检查第二种和第三种价格类型 (带有 priceToPay 类的 div)
            price_script = """
                let priceToPayElement = document.querySelector('.priceToPay .a-offscreen');
                if (priceToPayElement) {
                    return priceToPayElement.textContent.trim();
                }

                // 如果没有 offscreen 价格，尝试组合价格部分
                let priceWhole = document.querySelector('.priceToPay .a-price-whole');
                let priceFraction = document.querySelector('.priceToPay .a-price-fraction');
                if (priceWhole && priceFraction) {
                    return priceWhole.textContent.trim() + '.' + priceFraction.textContent.trim();
                }
                return null;
            """
            price_to_pay = self.driver.execute_script(price_script)
            if price_to_pay:
                # 清理价格文本
                price_match = re.search(r'\$?([\d,]+\.?\d*)', price_to_pay.replace('\n', ''))
                if price_match:
                    return float(price_match.group(1).replace(',', ''))

            # 备选方案：尝试其他常见的价格选择器
            # 3.1. 首先尝试获取 a-offscreen 中的完整价格
            price_elem = self.safe_find_element(By.CSS_SELECTOR, ".a-price .a-offscreen")
            if price_elem:
                price_text = price_elem.get_attribute('textContent')
                if price_text:
                    price = re.search(r'\$([\d,.]+)', price_text)
                    if price:
                        return float(price.group(1).replace(',', ''))

            # 3.2. 如果上面方法失败,尝试组合价格部分
            whole = self.safe_find_element(By.CSS_SELECTOR, ".a-price-whole")
            fraction = self.safe_find_element(By.CSS_SELECTOR, ".a-price-fraction")
            if whole and fraction:
                price_text = f"{whole.text}.{fraction.text}"
                try:
                    return float(price_text)
                except:
                    pass

            return 'N/A'

        except Exception as e:
            logger.error(f"Error extracting price: {str(e)}")
            return 'N/A'

    def _get_product_rating(self):
        try:
            # 1. 尝试从星级图标类名中提取
            star_elem = self.safe_find_element(By.CSS_SELECTOR, "[class*='a-size-base a-color-base']")
            if star_elem:
                class_name = star_elem.get_attribute('class')
                star_match = re.search(r'a-star-(\d-\d|\d)', class_name)
                if star_match:
                    rating = star_match.group(1).replace('-', '.')
                    return float(rating)

            # 2. 备选方案:从评分文本中提取
            rating_text = self.safe_find_element(By.CSS_SELECTOR, ".a-icon-alt")
            if rating_text:
                rating_match = re.search(r'([\d.]+) out of 5', rating_text.get_attribute('textContent'))
                if rating_match:
                    return float(rating_match.group(1))

            return 'N/A'
        except Exception as e:
            logger.error(f"Error extracting rating: {str(e)}")
            return 'N/A'

    def _get_review_count(self):
        """获取商品评论数量"""
        try:
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            matches = re.findall(r'(\d+(?:,\d+)?)\s*(?:[^\d\n]*\s+)?ratings?', page_text)
            if matches:
                return int(matches[0].replace(',', ''))

            return 'N/A'
        except Exception as e:
            logger.error(f"Error extracting review count: {str(e)}")
            return 'N/A'

    def _get_product_description(self):
        """获取商品完整描述信息"""
        try:
            description_parts = []
            seen_content = set()  # 用于去重

            # 1. 使用 JavaScript 获取描述内容
            js_script = """
                function getDescription() {
                    let descriptions = [];

                    // 获取产品描述
                    let productDesc = document.getElementById('productDescription');
                    if (productDesc) descriptions.push({type: 'Product Description', content: productDesc.innerText});

                    // 获取要点描述
                    let bullets = document.getElementById('feature-bullets');
                    if (bullets) descriptions.push({type: 'Key Features', content: bullets.innerText});

                    // 获取技术细节
                    let techDetails = document.getElementById('productDetails_techSpec_section_1');
                    if (techDetails) descriptions.push({type: 'Technical Details', content: techDetails.innerText});

                    // 获取产品详情
                    let productDetails = document.getElementById('detailBullets_feature_div');
                    if (productDetails) descriptions.push({type: 'Product Details', content: productDetails.innerText});

                    // 获取A+内容
                    let aplus = document.getElementById('aplus_feature_div');
                    if (aplus) descriptions.push({type: 'Additional Information', content: aplus.innerText});

                    // 获取产品概述
                    let overview = document.getElementById('productOverview_feature_div');
                    if (overview) descriptions.push({type: 'Product Overview', content: overview.innerText});

                    return descriptions;
                }
                return getDescription();
            """

            js_results = self.driver.execute_script(js_script)
            if js_results:
                for result in js_results:
                    if result['content'] and result['content'].strip():
                        content = self._clean_description_text(result['content'])
                        if content and content not in seen_content:
                            description_parts.append(f"{result['type']}:\n{content}")
                            seen_content.add(content)

            # 2. 使用配置的选择器获取描述内容
            for by_method, selector in ScraperConfig.DESCRIPTION_SELECTORS:
                try:
                    elements = self.driver.find_elements(getattr(By, by_method), selector)
                    for element in elements:
                        try:
                            # 获取元素的文本内容
                            content = element.get_attribute('textContent') or element.text
                            if content:
                                content = self._clean_description_text(content)
                                if content and content not in seen_content:
                                    # 尝试获取内容类型（标题或标签）
                                    content_type = self._get_content_type(element)
                                    if content_type:
                                        description_parts.append(f"{content_type}:\n{content}")
                                    else:
                                        description_parts.append(content)
                                    seen_content.add(content)
                        except:
                            continue
                except:
                    continue

            # 3. 组合并格式化描述内容
            if description_parts:
                # 使用双换行符分隔不同部分
                final_description = "\n\n".join(description_parts)
                # 限制长度但保持完整段落
                if len(final_description) > 32000:  # 设置一个合理的最大长度
                    final_description = self._truncate_to_last_complete_section(final_description, 32000)
                return final_description

            return 'N/A'

        except Exception as e:
            logger.error(f"Error getting product description: {str(e)}")
            return 'N/A'

    def _clean_description_text(self, text):
        """清理和格式化描述文本"""
        if not text:
            return None

        try:
            # 基本清理
            text = text.strip()
            # 替换多个空白字符为单个空格
            text = re.sub(r'\s+', ' ', text)
            # 替换多个换行为双换行
            text = re.sub(r'\n\s*\n\s*\n*', '\n\n', text)
            # 移除特殊字符但保留基本标点
            text = re.sub(r'[^\w\s.,;:!?()\'"\-–—/\n]', '', text)
            # 移除重复的标点符号
            text = re.sub(r'([.,!?])\1+', r'\1', text)
            # 确保段落之间有适当的间距
            text = re.sub(r'([.!?])\s*(\w)', r'\1\n\2', text)

            # 移除常见的无用文本
            useless_patterns = [
                r'Read more',
                r'Show more',
                r'See more',
                r'Click to open expanded view',
                r'Scroll left/right to see more',
                r'Roll over image to zoom in',
            ]
            for pattern in useless_patterns:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)

            # 最终清理
            text = text.strip()
            return text if text else None

        except Exception as e:
            logger.warning(f"Error cleaning description text: {str(e)}")
            return text.strip() if text else None

    def _get_content_type(self, element):
        """获取描述内容的类型"""
        try:
            # 检查元素的ID和class来确定内容类型
            element_id = element.get_attribute('id') or ''
            element_class = element.get_attribute('class') or ''

            type_indicators = {
                'feature-bullets': 'Key Features',
                'productDescription': 'Product Description',
                'technical': 'Technical Details',
                'detail': 'Product Details',
                'specification': 'Specifications',
                'overview': 'Product Overview',
                'aplus': 'Additional Information',
                'important': 'Important Information'
            }

            for indicator, content_type in type_indicators.items():
                if indicator in element_id.lower() or indicator in element_class.lower():
                    return content_type

            # 检查父元素
            parent = element.find_element(By.XPATH, '..')
            parent_id = parent.get_attribute('id') or ''
            parent_class = parent.get_attribute('class') or ''

            for indicator, content_type in type_indicators.items():
                if indicator in parent_id.lower() or indicator in parent_class.lower():
                    return content_type

            return None

        except:
            return None

    def _truncate_to_last_complete_section(self, text, max_length):
        """在不切断段落的情况下截断文本"""
        if len(text) <= max_length:
            return text

        # 找到最后一个完整段落的位置
        last_paragraph = max_length
        for separator in ['\n\n', '. ', '! ', '? ']:
            pos = text.rfind(separator, 0, max_length)
            if pos > 0:
                last_paragraph = pos + len(separator)
                break

        return text[:last_paragraph].strip()

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
                self.driver.get(url['url'] if isinstance(url, dict) else url)
                logger.info("Successfully navigated to URL")

                self.random_sleep()

                if self._check_and_handle_throttling():
                    logger.info("Throttling detected, will retry...")
                    retries += 1
                    self.random_sleep(3, 5)
                    continue

                return True

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

            # 等待价格元素加载 - 增加多个选择器
            price_loaded = False
            for selector in ['.a-price', '.a-offscreen', '#priceblock_ourprice']:
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    price_loaded = True
                    break
                except:
                    continue

            if not price_loaded:
                logger.warning("Price element not found, proceeding anyway...")

            # 添加短暂滚动以触发动态内容加载
            self.driver.execute_script("window.scrollTo(0, 200)")
            self.random_sleep(1, 2)

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

            # 使用JavaScript获取所有产品链接及其排名
            ranked_products = []
            script = """
                let products = [];
                let rankElements = document.querySelectorAll('.zg-bdg-text, [class*="zg-badge-text"]');

                rankElements.forEach(rankElem => {
                    let rank = parseInt(rankElem.textContent.match(/\\d+/)[0]);
                    let productCard = rankElem.closest('[class*="zg-item"], [class*="zg-grid-item"]');
                    if (productCard) {
                        let link = productCard.querySelector('a[href*="/dp/"]');
                        if (link && link.href) {
                            let match = link.href.match(/\/dp\/([A-Z0-9]{10})/);
                            if (match) {
                                products.push({
                                    rank: rank,
                                    url: 'https://www.amazon.com/dp/' + match[1]
                                });
                            }
                        }
                    }
                });

                // 按排名排序
                products.sort((a, b) => a.rank - b.rank);
                return products;
            """

            try:
                ranked_products = self.driver.execute_script(script)
            except Exception as e:
                logger.error(f"Error executing JavaScript for ranked products: {str(e)}")
                # 如果JavaScript方法失败，使用备选方法
                ranked_products = self._get_ranked_products_fallback()

            if not ranked_products:
                logger.warning("No ranked products found with primary method, trying fallback...")
                ranked_products = self._get_ranked_products_fallback()

            # 确保结果按排名排序并限制数量
            ranked_products = sorted(ranked_products, key=lambda x: x['rank'])[:ScraperConfig.MAX_PRODUCTS_PER_CATEGORY]

            # 提取URL列表
            unique_links = [product['url'] for product in ranked_products]

            logger.info(f"Found {len(unique_links)} ranked products")
            for product in ranked_products:
                logger.info(f"Rank {product['rank']}: {product['url']}")

            return unique_links

        except Exception as e:
            logger.error(f"Error getting bestsellers: {str(e)}")
            return []

    def _get_ranked_products_fallback(self):
        """备选方法：使用传统的DOM遍历获取排名产品"""
        ranked_products = []
        try:
            # 尝试不同的排名和产品容器选择器
            rank_selectors = [
                '.zg-bdg-text',
                '[class*="zg-badge-text"]',
                '.zg-ranking',
                '[class*="zg-rank"]'
            ]

            for rank_selector in rank_selectors:
                rank_elements = self.driver.find_elements(By.CSS_SELECTOR, rank_selector)
                for rank_elem in rank_elements:
                    try:
                        # 获取排名
                        rank_text = rank_elem.text.strip()
                        rank_match = re.search(r'\d+', rank_text)
                        if not rank_match:
                            continue
                        rank = int(rank_match.group())

                        # 从排名元素向上查找产品容器
                        product_card = rank_elem
                        for _ in range(5):  # 最多向上查找5层父元素
                            product_card = product_card.find_element(By.XPATH, '..')
                            link = None
                            try:
                                link = product_card.find_element(By.CSS_SELECTOR, 'a[href*="/dp/"]')
                                if link:
                                    break
                            except:
                                continue

                        if link:
                            url = link.get_attribute('href')
                            match = re.search(r'/dp/([A-Z0-9]{10})', url)
                            if match:
                                ranked_products.append({
                                    'rank': rank,
                                    'url': f'https://www.amazon.com/dp/{match.group(1)}'
                                })

                    except Exception as e:
                        logger.debug(f"Error processing individual rank element: {str(e)}")
                        continue

                if ranked_products:
                    break

        except Exception as e:
            logger.error(f"Error in fallback ranked products method: {str(e)}")

        return ranked_products

    def _validate_product_order(self, products):
        """验证产品顺序的正确性"""
        if not products:
            return False

        # 检查排名是否连续
        ranks = [p.get('rank') for p in products]
        expected_ranks = list(range(1, len(ranks) + 1))

        if ranks != expected_ranks:
            logger.warning(f"Product ranks are not sequential: {ranks}")
            return False

        return True

    def get_search_results(self, search_url, max_retries=5):
        """获取搜索结果中的商品链接"""
        retry_count = 0
        while retry_count < max_retries:
            try:
                if not self._handle_page_with_retry(search_url):
                    retry_count += 1
                    logger.warning(f"Failed to load page, attempt {retry_count}/{max_retries}")
                    continue

                # 执行页面滚动来加载更多内容，确保加载足够多的结果
                self._scroll_until_enough_results()

                # 等待搜索结果加载
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.s-result-item'))
                    )
                except TimeoutException:
                    logger.warning(f"Timeout waiting for search results, attempt {retry_count + 1}/{max_retries}")
                    if retry_count < max_retries - 1:
                        logger.info("Refreshing page...")
                        self.driver.refresh()
                        self.random_sleep(3, 5)
                        retry_count += 1
                        continue

                # 使用更精确的JavaScript脚本来获取排序后的产品链接
                script = """
                    function getProducts() {
                        let products = [];
                        // 获取所有搜索结果项
                        let resultItems = Array.from(document.querySelectorAll('[data-component-type="s-search-result"]'));

                        // 对结果项进行处理
                        resultItems.forEach((item, index) => {
                            // 获取排名信息（如果有的话）
                            let rankElem = item.querySelector('.zg-badge-text') || 
                                         item.querySelector('[class*="zg-badge"]') ||
                                         item.querySelector('.zg-rank');
                            let rank = rankElem ? parseInt(rankElem.textContent.match(/\\d+/)[0]) : (index + 1);

                            // 获取产品链接
                            let link = item.querySelector('a[href*="/dp/"]');
                            if (link) {
                                let url = link.href;
                                let asinMatch = url.match(/\/dp\/([A-Z0-9]{10})/);
                                if (asinMatch) {
                                    // 检查是否为赞助商品
                                    let isSponsored = item.querySelector('[data-component-type="sp-sponsored-result"]') !== null;
                                    if (!isSponsored) {
                                        products.push({
                                            rank: rank,
                                            url: 'https://www.amazon.com/dp/' + asinMatch[1],
                                            asin: asinMatch[1]
                                        });
                                    }
                                }
                            }
                        });

                        // 按排名排序
                        products.sort((a, b) => a.rank - b.rank);

                        // 只返回指定数量的产品
                        return products.slice(0, arguments[0]);
                    }
                    return getProducts(arguments[0]);
                """

                product_links = self.driver.execute_script(script, ScraperConfig.MAX_PRODUCTS_PER_CATEGORY)

                if not product_links:
                    logger.warning(
                        f"No product links found with primary method (attempt {retry_count + 1}/{max_retries})")
                    if retry_count < max_retries - 1:
                        logger.info("Trying fallback method...")
                        fallback_links = self._get_search_results_fallback()
                        if fallback_links:
                            product_links = fallback_links[:ScraperConfig.MAX_PRODUCTS_PER_CATEGORY]
                        else:
                            self.driver.refresh()
                            self.random_sleep(3, 5)
                            retry_count += 1
                            continue

                # 确保没有重复的ASIN
                unique_links = []
                seen_asins = set()
                for product in product_links:
                    if product['asin'] not in seen_asins:
                        seen_asins.add(product['asin'])
                        unique_links.append(product['url'])
                        if len(unique_links) >= ScraperConfig.MAX_PRODUCTS_PER_CATEGORY:
                            break

                if unique_links:
                    logger.info(f"Found {len(unique_links)} unique products from search results")
                    for i, link in enumerate(unique_links, 1):
                        logger.info(f"Product {i}: {link}")
                    return unique_links[:ScraperConfig.MAX_PRODUCTS_PER_CATEGORY]

                logger.warning(f"No products found after attempt {retry_count + 1}/{max_retries}")
                retry_count += 1

            except Exception as e:
                logger.error(f"Error getting search results (attempt {retry_count + 1}/{max_retries}): {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    self.random_sleep(3, 5)

        logger.error(f"Failed to get search results after {max_retries} attempts")
        return []

    def _scroll_until_enough_results(self):
        """滚动页面直到获取足够数量的结果"""
        max_scroll_attempts = 10
        scroll_attempt = 0
        previous_height = 0

        while scroll_attempt < max_scroll_attempts:
            # 获取当前有效的搜索结果数量
            valid_results = len(self.driver.find_elements(By.CSS_SELECTOR,
                                                          '[data-component-type="s-search-result"]:not([data-component-type="sp-sponsored-result"])'))

            if valid_results >= ScraperConfig.MAX_PRODUCTS_PER_CATEGORY:
                logger.info(f"Found enough results: {valid_results}")
                break

            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.random_sleep(1, 2)

            # 检查是否已经到达底部
            current_height = self.driver.execute_script("return document.body.scrollHeight")
            if current_height == previous_height:
                logger.info("Reached bottom of page")
                break

            previous_height = current_height
            scroll_attempt += 1

            # 等待新内容加载
            self.random_sleep(1, 2)

    def _get_search_results_fallback(self):
        """备用方法：使用多种选择器组合获取搜索结果"""
        products = []
        try:
            # 多层选择器组合
            selector_combinations = [
                # 组合1：标准搜索结果
                {'container': '[data-component-type="s-search-result"]', 'link': 'a[href*="/dp/"]'},
                # 组合2：结果项
                {'container': '.s-result-item[data-asin]', 'link': 'a.a-link-normal[href*="/dp/"]'},
                # 组合3：网格布局
                {'container': '.sg-col-inner', 'link': 'a.a-text-normal[href*="/dp/"]'},
                # 组合4：备用布局
                {'container': '.s-include-content-margin', 'link': 'a.a-link-normal[href*="/dp/"]'}
            ]

            for selectors in selector_combinations:
                try:
                    # 等待容器元素出现
                    containers = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selectors['container']))
                    )

                    for container in containers:
                        if len(products) >= ScraperConfig.MAX_PRODUCTS_PER_CATEGORY:
                            break

                        try:
                            link = container.find_element(By.CSS_SELECTOR, selectors['link'])
                            url = link.get_attribute('href')
                            if url:
                                match = re.search(r'/dp/([A-Z0-9]{10})', url)
                                if match:
                                    asin = match.group(1)
                                    if not any(asin in p['url'] for p in products):
                                        products.append({
                                            'url': f'https://www.amazon.com/dp/{asin}'
                                        })
                        except:
                            continue

                    if products:
                        break

                except TimeoutException:
                    continue

            # 如果还是没有找到产品，尝试直接查找所有包含 dp 的链接
            if not products:
                all_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/dp/"]')
                seen_asins = set()

                for link in all_links:
                    if len(products) >= ScraperConfig.MAX_PRODUCTS_PER_CATEGORY:
                        break

                    try:
                        url = link.get_attribute('href')
                        if url:
                            match = re.search(r'/dp/([A-Z0-9]{10})', url)
                            if match and match.group(1) not in seen_asins:
                                seen_asins.add(match.group(1))
                                products.append({
                                    'url': f'https://www.amazon.com/dp/{match.group(1)}'
                                })
                    except:
                        continue

        except Exception as e:
            logger.error(f"Error in fallback search results method: {str(e)}")

        return products

    def run(self, search_url=None):
        """运行爬虫"""
        try:
            self.products = []
            # 获取搜索结果中的商品链接
            product_links = self.get_search_results(search_url)

            # 提取搜索关键词作为类别名称
            search_term = re.search(r'k=([^&]+)', search_url)
            self.category_name = unquote(search_term.group(1)).replace('+', ' ') if search_term else "Search_Results"

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