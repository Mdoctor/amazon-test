# Amazon商品数据采集器

这是一个基于Python的高性能亚马逊商品数据并行采集工具。该工具专门设计用于同时从多个亚马逊类别页面高效采集商品信息。

## 主要特性

- 多进程并行采集，提高效率
- 灵活的配置参数系统
- 完善的错误处理和日志记录
- 自动化的浏览器驱动管理
- 支持多种数据采集模式（搜索结果、畅销商品等）
- 智能的反爬虫策略
- 自动化的数据存储和格式化

## 环境要求

- Python 3.11+
- Chrome浏览器
- 相关Python依赖包（见requirements.txt）
- 稳定的网络连接

## 安装步骤

1. 克隆代码仓库：
```bash
git clone <仓库地址>
cd amazon-test
```

2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 配置说明

通过`config.py`文件配置采集参数：

- `HEADLESS`: 无头浏览器模式（True/False）
- `MAX_PRODUCTS_PER_CATEGORY`: 每个类别采集的商品数量
- `MAX_WORKERS`: 最大并行进程数
- `CHUNK_SIZE`: 每个进程处理的产品数量
- `WAIT_TIME`: 页面加载等待时间
- `MIN_SLEEP`/`MAX_SLEEP`: 随机延迟范围
- `SCROLL_STEPS`: 页面滚动次数
- `WINDOW_SIZE`: 浏览器窗口大小

## 使用方法

1. 基本用法：
```python
from parallel_scraper import ParallelScraper

# 定义搜索关键词
search_terms = [
    "apple",
    "laptop"
]

# 运行采集
parallel_scraper = ParallelScraper(max_workers=4)
results = parallel_scraper.run_parallel(search_terms)
```

2. 命令行运行：
```bash
python main.py
```

## 项目结构

```
amazon-test/
├── main.py              # 程序入口
├── parallel_scraper.py  # 并行采集实现
├── scraper.py          # 核心采集逻辑
├── config.py           # 配置文件
├── logger.py           # 日志管理
├── driver_manager.py   # 浏览器驱动管理
├── data_saver.py       # 数据保存
├── requirements.txt    # 项目依赖
└── README.md          # 项目文档
```

## 数据采集内容

每个商品的采集信息包括：
- 商品标题
- 价格信息（当前价格、原价、促销价等）
- 商品评分和评论数
- 商品描述
- 商品图片URL
- 品牌信息
- 商品可用性状态
- 商品分类
- ASIN编号
- 采集时间戳

## 数据存储

- 支持Excel格式保存
- 自动文件命名和分类
- 数据格式化和样式优化
- CSV备份机制

## 错误处理

包含完善的错误处理机制：
- 自动重试机制
- 详细的错误日志
- 异常状态恢复
- 网络超时处理
- 反爬虫策略应对

## 日志系统

通过`logger.py`实现全面的日志记录：
- 采集进度跟踪
- 成功/失败统计
- 详细错误信息
- 性能监控数据

## 注意事项

1. 本工具仅供学习和研究使用
2. 使用时请遵守亚马逊的服务条款和robots.txt规则
3. 建议合理配置采集参数，避免对目标网站造成压力
4. 采集数据请勿用于商业用途

## 常见问题

1. 浏览器驱动相关问题
2. 网络连接超时处理
3. 数据保存格式调整
4. 采集参数优化建议

## 贡献指南

1. Fork本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 技术支持

如有问题或建议，请在仓库中创建issue。