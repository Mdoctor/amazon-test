import undetected_chromedriver as uc
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from config import ScraperConfig
from logger import logger
import atexit


class DriverManager:
    def __init__(self):
        self.driver = None
        self.wait = None
        # 注册退出时的清理函数
        atexit.register(self.quit)

    def setup_driver(self, headless=False):
        """配置并初始化Chrome驱动"""
        try:
            options = uc.ChromeOptions()
            self._configure_chrome_options(options, headless)
            self.driver = uc.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, ScraperConfig.WAIT_TIME)
            self._setup_anti_detection()
            logger.info(f"Chrome driver setup successful with {'headless' if headless else 'normal'} mode")
            return self.driver, self.wait
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {str(e)}")
            raise

    def _configure_chrome_options(self, options, headless=False):
        """配置Chrome选项"""
        # 基本设置
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')

        # 只在 headless=True 时添加无头模式配置
        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-setuid-sandbox')
            options.add_argument('--disable-software-rasterizer')

        # 设置窗口大小
        options.add_argument(f'--window-size={ScraperConfig.WINDOW_SIZE[0]},{ScraperConfig.WINDOW_SIZE[1]}')
        options.add_argument('--incognito')
        options.add_argument('--disable-blink-features=AutomationControlled')

        # 随机User-Agent
        ua = UserAgent()
        options.add_argument(f'--user-agent={ua.random}')

    def _setup_anti_detection(self):
        """设置反检测JavaScript"""
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """)

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