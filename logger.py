import logging
import os
from datetime import datetime
import atexit

# 使用模块级变量来跟踪logger是否已经被初始化
_logger = None
_log_file = None


def get_logger():
    global _logger, _log_file

    # 如果logger已经初始化，直接返回
    if _logger is not None:
        return _logger

    # 创建logger
    _logger = logging.getLogger('amazon_scraper')
    _logger.setLevel(logging.INFO)

    # 如果logger已经有handlers，说明已经配置过，直接返回
    if _logger.handlers:
        return _logger

    # 创建日志文件名
    timestamp = datetime.now().strftime('%Y%m%d')
    _log_file = f'logs/scraper_{timestamp}.log'

    # 确保logs目录存在
    os.makedirs('logs', exist_ok=True)

    # 创建文件处理器
    file_handler = logging.FileHandler(_log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - [%(threadName)s] - %(levelname)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    # 设置格式化器
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 添加处理器
    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)

    # 注册程序退出时的清理函数
    def cleanup():
        # 如果存在空的日志文件，删除它
        if _log_file and os.path.exists(_log_file) and os.path.getsize(_log_file) == 0:
            try:
                os.remove(_log_file)
            except:
                pass

        # 关闭所有处理器
        for handler in _logger.handlers[:]:
            handler.close()
            _logger.removeHandler(handler)

    atexit.register(cleanup)

    return _logger


# 创建一个默认的logger实例
logger = get_logger()