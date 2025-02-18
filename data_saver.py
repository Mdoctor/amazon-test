import os
import time
import re
import pandas as pd
from logger import logger


class DataSaver:
    OUTPUT_DIR = 'scraper_excel'
    FINAL_OUTPUT_DIR = 'output_excel'

    @staticmethod
    def save_to_excel(products, category_name):
        """保存商品信息到Excel文件，适配WooCommerce格式"""
        try:
            if not products:
                logger.warning("No products to save")
                return None

            # 创建输出目录
            os.makedirs(DataSaver.OUTPUT_DIR, exist_ok=True)
            os.makedirs(DataSaver.FINAL_OUTPUT_DIR, exist_ok=True)

            # 准备WooCommerce所需的列
            woo_columns = [
                'Title', 'Description', 'Short description', 'Regular price', 'Sale_Price',
                'Category', 'Images', 'SKU', 'Sizes', 'Color'
            ]

            # 转换数据为WooCommerce格式
            woo_data = []
            for product in products:
                # 提取价格信息
                regular_price = product['price']['original_price']
                if regular_price == 'N/A':
                    regular_price = product['price']['current_price']

                sale_price = product['price']['current_price'] if product['price'][
                                                                      'current_price'] != regular_price else ''

                # 提取尺寸信息（从描述中查找）
                sizes = DataSaver._extract_sizes(product['description'])

                # 提取颜色信息（从描述中查找）
                colors = DataSaver._extract_colors(product['description'])

                # 生成简短描述（取描述的前100个字符）
                short_description = DataSaver._create_short_description(product['description'])

                # 处理图片URL
                image_url = product['image_url'].replace('fmt=webp', 'fmt=jpg') if product['image_url'] != 'N/A' else ''

                # 生成SKU
                sku = f"{product['asin']}" if product['asin'] != 'N/A' else ''

                woo_data.append({
                    'Title': product['title'],
                    'Description': product['description'],
                    'Short description': short_description,
                    'Regular price': regular_price,
                    'Sale_Price': sale_price,
                    'Category': product['category'],
                    'Images': image_url,
                    'SKU': sku,
                    'Sizes': ','.join(sizes) if sizes else '',
                    'Color': ','.join(colors) if colors else 'As shown in the figure',
                })

            # 创建DataFrame
            df = pd.DataFrame(woo_data, columns=woo_columns)

            # 保存文件
            safe_category_name = re.sub(r'[<>:"/\\|?*]', '_', category_name)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f'{safe_category_name}_products_{timestamp}.csv'
            full_path = os.path.join(DataSaver.OUTPUT_DIR, filename)

            # 保存为CSV格式
            df.to_csv(full_path, index=False, encoding='utf-8-sig')
            logger.info(f"Successfully saved to {full_path}")

            return full_path

        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            return None

    @staticmethod
    def _extract_sizes(description):
        """从描述中提取尺寸信息"""
        size_patterns = [
            r'Size:?\s*((?:X?S|X?M|X?L|XXL|XXXL|2XL|3XL|4XL|5XL)(?:\s*,\s*(?:X?S|X?M|X?L|XXL|XXXL|2XL|3XL|4XL|5XL))*)',
            r'Available sizes?:?\s*((?:\d+(?:\.\d+)?(?:\s*,\s*\d+(?:\.\d+)?)*))(?:\s*(?:cm|inch|inches|"|\'|mm))?',
            r'Sizes?(?:\s+available)?:?\s*((?:Small|Medium|Large|X-Large|XX-Large)(?:\s*,\s*(?:Small|Medium|Large|X-Large|XX-Large))*)',
        ]

        sizes = set()
        if description and description != 'N/A':
            for pattern in size_patterns:
                matches = re.findall(pattern, description, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, str):
                        sizes.update(size.strip() for size in match.split(','))

        return sorted(list(sizes)) if sizes else []

    @staticmethod
    def _extract_colors(description):
        """从描述中提取颜色信息"""
        color_patterns = [
            r'Colou?rs?:?\s*((?:[A-Za-z]+(?:\s+[A-Za-z]+)*(?:\s*,\s*[A-Za-z]+(?:\s+[A-Za-z]+)*)*))(?:\.|$|\n)',
            r'Available colou?rs?:?\s*((?:[A-Za-z]+(?:\s+[A-Za-z]+)*(?:\s*,\s*[A-Za-z]+(?:\s+[A-Za-z]+)*)*))(?:\.|$|\n)',
        ]

        colors = set()
        if description and description != 'N/A':
            for pattern in color_patterns:
                matches = re.findall(pattern, description, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, str):
                        colors.update(color.strip() for color in match.split(','))

        return sorted(list(colors)) if colors else []

    @staticmethod
    def _create_short_description(description):
        """创建简短描述"""
        if description and description != 'N/A':
            # 移除HTML标签
            clean_desc = re.sub(r'<[^>]+>', '', description)
            # 取前100个字符
            short_desc = clean_desc[:100].strip()
            # 确保不会截断单词
            if len(clean_desc) > 100:
                last_space = short_desc.rfind(' ')
                if last_space > 0:
                    short_desc = short_desc[:last_space] + '...'
                else:
                    short_desc += '...'
            return short_desc
        return ''