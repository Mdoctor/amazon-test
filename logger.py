import logging
from logging.handlers import RotatingFileHandler


def setup_logger():
    """配置并返回logger实例"""
    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # 创建 RotatingFileHandler，maxBytes=0 表示不限制单个文件大小，backupCount=0 表示不保留备份
    file_handler = RotatingFileHandler(
        'scraper.log',
        mode='w',
        maxBytes=0,
        backupCount=0,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 配置 logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # 清除可能存在的旧处理器
    logger.handlers.clear()

    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()