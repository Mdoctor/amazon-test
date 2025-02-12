import os
import time
import re
import pandas as pd
from logger import logger


class DataSaver:
    @staticmethod
    def save_to_excel(products, category_name):
        """保存商品信息到Excel文件"""
        try:
            if not products:
                logger.warning("No products to save")
                return

            # 准备数据
            safe_category_name = re.sub(r'[<>:"/\\|?*]', '_', category_name)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f'{safe_category_name}_bestsellers_{timestamp}.xlsx'

            # 创建DataFrame，包含所有字段
            df = pd.DataFrame([
                {
                    'Rank': i + 1,
                    'ASIN': p['asin'],
                    'Title': p['title'],
                    'Brand': p['brand'],
                    'Price': p['price'],
                    'Rating': p['rating'],
                    'Review Count': p['review_count'],
                    'Availability': p['availability'],
                    'Description': p['description'],
                    'Image URL': p['image_url'],
                    'Product URL': p['url'],
                    'Category': p['category'],
                    'Timestamp': p['timestamp']
                }
                for i, p in enumerate(products)
            ])

            # 尝试保存文件
            DataSaver._try_save_file(df, filename)

        except Exception as e:
            logger.error(f"Error saving to Excel: {str(e)}")
            DataSaver._save_as_csv_backup(df, safe_category_name, timestamp)

    @staticmethod
    def _try_save_file(df, filename):
        """尝试在不同位置保存文件"""
        possible_dirs = [
            '.',
            os.path.expanduser('~'),
            os.path.join(os.path.expanduser('~'), 'Documents'),
            os.getenv('TEMP', os.path.expanduser('~'))
        ]

        for save_dir in possible_dirs:
            try:
                full_path = os.path.join(save_dir, filename)
                DataSaver._save_with_formatting(df, full_path)
                logger.info(f"Successfully saved to {full_path}")
                return
            except Exception as e:
                logger.warning(f"Error saving to {save_dir}: {str(e)}")
                continue

        raise Exception("Unable to save file in any of the attempted locations")

    @staticmethod
    def _save_with_formatting(df, full_path):
        """保存Excel文件并设置格式"""
        # 确保价格列的数据类型为字符串
        if 'Price' in df.columns:
            df['Price'] = df['Price'].astype(str)

        with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Bestsellers')
            worksheet = writer.sheets['Bestsellers']

            # 获取价格列的索引
            try:
                price_col_idx = df.columns.get_loc('Price') + 1  # Excel列从1开始

                # 设置价格列格式为文本，保持原始格式
                for row in range(2, len(df) + 2):  # 从第2行开始（跳过标题行）
                    cell = worksheet.cell(row=row, column=price_col_idx)
                    cell.number_format = '@'  # 设置为文本格式

                # 设置标题行的格式
                header_cell = worksheet.cell(row=1, column=price_col_idx)
                header_cell.number_format = '@'
            except ValueError:
                logger.warning("Price column not found in DataFrame")

            # 自动调整列宽
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                # 限制最大列宽为50个字符
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)

    @staticmethod
    def _save_as_csv_backup(df, category_name, timestamp):
        """作为备份保存为CSV文件"""
        try:
            csv_filename = f'{category_name}_bestsellers_{timestamp}.csv'
            csv_path = os.path.join(os.getenv('TEMP', '.'), csv_filename)
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            logger.info(f"Saved data as CSV instead at: {csv_path}")
        except Exception as csv_error:
            logger.error(f"Failed to save as CSV as well: {str(csv_error)}")
