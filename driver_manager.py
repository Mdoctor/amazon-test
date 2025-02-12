import undetected_chromedriver as uc
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from config import ScraperConfig
from logger import logger
import atexit
import time
import random


class DriverManager:
    def __init__(self):
        self.driver = None
        self.wait = None
        # 注册退出时的清理函数
        atexit.register(self.quit)

    def setup_driver(self, headless=False, max_retries=3):
        """配置并初始化Chrome驱动，添加重试机制"""
        retry_count = 0
        while retry_count < max_retries:
            try:
                options = uc.ChromeOptions()
                self._configure_chrome_options(options, headless)

                # 添加代理服务器设置
                # options.add_argument('--proxy-server=http://your-proxy-server:port')

                self.driver = uc.Chrome(options=options)
                self.wait = WebDriverWait(self.driver, ScraperConfig.WAIT_TIME)
                self._setup_anti_detection()
                logger.info(f"Chrome driver setup successful with {'headless' if headless else 'normal'} mode")
                return self.driver, self.wait

            except Exception as e:
                retry_count += 1
                logger.warning(f"Attempt {retry_count}/{max_retries} failed to setup Chrome driver: {str(e)}")

                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None

                if retry_count < max_retries:
                    # 指数退避策略
                    sleep_time = (2 ** retry_count) + random.uniform(0, 1)
                    logger.info(f"Waiting {sleep_time:.2f} seconds before retrying...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Failed to setup Chrome driver after {max_retries} attempts")
                    raise

    def _configure_chrome_options(self, options, headless=False):
        """配置Chrome选项"""
        # 基本设置
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')

        # 只在 headless=True 时添加无头模式配置
        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-setuid-sandbox')
            options.add_argument('--disable-software-rasterizer')

        # 设置窗口大小
        options.add_argument(f'--window-size={ScraperConfig.WINDOW_SIZE[0]},{ScraperConfig.WINDOW_SIZE[1]}')
        options.add_argument('--incognito')
        options.add_argument('--disable-blink-features=AutomationControlled')

        # 设置页面加载策略
        options.page_load_strategy = 'normal'

        try:
            # 随机User-Agent
            ua = UserAgent()
            options.add_argument(f'--user-agent={ua.random}')
        except Exception as e:
            logger.warning(f"Failed to set random user agent: {str(e)}")
            # 使用默认 user agent
            options.add_argument(
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    def _setup_anti_detection(self):
        """设置反检测JavaScript"""
        try:
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            """)
        except Exception as e:
            logger.warning(f"Failed to setup anti-detection: {str(e)}")

    def quit(self):
        """安全关闭驱动"""
        if hasattr(self, 'driver') and self.driver:
            try:
                # 确保所有窗口都关闭
                if getattr(self.driver, 'window_handles', None):
                    self.driver.close()
                self.driver.quit()
                self.driver = None
            except Exception as e:
                logger.warning(f"Error in driver cleanup: {str(e)}")