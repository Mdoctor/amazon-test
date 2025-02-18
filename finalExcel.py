import time
import pandas as pd
import random
import os
from logger import logger


def try_read_csv(file_path):
    """尝试使用不同编码格式读取CSV文件"""
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb18030', 'iso-8859-1']

    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            logger.info(f"Successfully read file with {encoding} encoding")
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.error(f"Error with {encoding} encoding: {str(e)}")
            continue

    raise ValueError("Unable to read file with any common encoding")


def generate_unique_random_ids(count, length=5):
    """生成指定数量的唯一随机ID"""
    return random.sample(range(10 ** (length - 1), 10 ** length), count)


def process_excel(input_file_path, output_dir):
    """处理Excel文件并转换为WooCommerce格式"""
    try:
        logger.info(f"Starting to process file: {input_file_path}")

        # 读取原始Excel文件
        df = try_read_csv(input_file_path)

        # 创建WooCommerce需要的字段
        columns = [
            'ID', 'Type', 'SKU', 'Name', 'Published', 'Is featured?', 'Visibility in catalog',
            'Short description', 'Description', 'Date sale price starts', 'Date sale price ends',
            'Tax status', 'Tax class', 'In stock?', 'Stock', 'Low stock amount',
            'Backorders allowed?', 'Sold individually?', 'Weight (kg)', 'Length (cm)',
            'Width (cm)', 'Height (cm)', 'Allow customer reviews?', 'Purchase note',
            'Sale price', 'Regular price', 'Categories', 'Tags', 'Shipping class',
            'Images', 'Download limit', 'Download expiry days', 'Parent', 'Grouped products',
            'Upsells', 'Cross-sells', 'External URL', 'Button text', 'Position',
            'Attribute 1 name', 'Attribute 1 value(s)', 'Attribute 1 visible',
            'Attribute 1 global', 'Attribute 2 name', 'Attribute 2 value(s)',
            'Attribute 2 visible', 'Attribute 2 global'
        ]

        # 创建空的DataFrame
        woo_df = pd.DataFrame(columns=columns)
        rows_to_add = []

        # 处理每个产品
        for _, row in df.iterrows():
            # 处理图片链接
            images = row['Images'].replace('fmt=webp', 'fmt=jpg') if pd.notna(row['Images']) else ''

            # 确定产品类型
            product_type = 'variable' if pd.notna(row['Sizes']) and row['Sizes'] else 'simple'

            # 处理颜色值
            color_value = row['Color'] if pd.notna(row['Color']) and row['Color'] != '' else 'As shown in the figure'

            # 处理描述
            short_description = row['Short description'] if pd.notna(row['Short description']) else ''

            # 处理SKU
            sku_value = row['SKU'] if pd.notna(row['SKU']) else ''

            # 创建基础产品
            base_product = {
                'ID': '',
                'Type': product_type,
                'SKU': sku_value,
                'Name': row['Title'],
                'Published': 1,
                'Is featured?': 0,
                'Visibility in catalog': 'visible',
                'Short description': short_description,
                'Description': row['Description'],
                'Sale price': row['Sale_Price'] if pd.notna(row['Sale_Price']) else '',
                'Regular price': row['Regular price'],
                'Categories': row['Category'] if pd.notna(row['Category']) else 'Uncategorized',
                'Images': images,
                'Attribute 1 name': 'Size' if product_type == 'variable' else '',
                'Attribute 1 value(s)': row['Sizes'] if pd.notna(row['Sizes']) else '',
                'Attribute 1 visible': 1 if product_type == 'variable' else '',
                'Attribute 1 global': 1 if product_type == 'variable' else '',
                'Attribute 2 name': 'Color',
                'Attribute 2 value(s)': color_value,
                'Attribute 2 visible': 1,
                'Attribute 2 global': 1
            }
            rows_to_add.append(base_product)

            # 处理变体
            if product_type == 'variable':
                sizes = row['Sizes'].split(',') if pd.notna(row['Sizes']) else []
                colors = row['Color'].split(',') if pd.notna(row['Color']) else [color_value]
                base_sale_price = row['Sale_Price'] if pd.notna(row['Sale_Price']) else row['Regular price']
                base_regular_price = row['Regular price']

                for size in sizes:
                    for color in colors:
                        variant = {
                            'ID': '',
                            'Type': 'variation',
                            'SKU': '',
                            'Name': row['Title'],
                            'Published': 1,
                            'Parent': row['Title'],
                            'Sale price': base_sale_price,
                            'Regular price': base_regular_price,
                            'Attribute 1 name': 'Size',
                            'Attribute 1 value(s)': size.strip(),
                            'Attribute 1 visible': 1,
                            'Attribute 1 global': 1,
                            'Attribute 2 name': 'Color',
                            'Attribute 2 value(s)': color.strip(),
                            'Attribute 2 visible': 1,
                            'Attribute 2 global': 1
                        }
                        rows_to_add.append(variant)

        # 将所有行添加到DataFrame
        woo_df = pd.concat([woo_df, pd.DataFrame(rows_to_add)], ignore_index=True)

        # 生成并分配唯一ID
        unique_ids = generate_unique_random_ids(len(woo_df))
        woo_df['ID'] = unique_ids

        # 设置库存和可见性
        woo_df['In stock?'] = 1000
        woo_df['Visibility in catalog'] = 'visible'

        # 处理变体关系
        variable_id = None
        product_name = None

        for index, row in woo_df.iterrows():
            if row['Type'] == 'variable':
                variable_id = row['ID']
                product_name = row['Name']
                woo_df.at[index, 'Regular price'] = ''
            elif row['Type'] == 'variation' and variable_id is not None:
                woo_df.at[index, 'Parent'] = f"id:{variable_id}"
                attribute_value = row['Attribute 1 value(s)']
                woo_df.at[index, 'Name'] = f"{product_name} - {attribute_value}"

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 保存文件
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_filename = f'updated_wc_product_export_with_multiple_products_{timestamp}.csv'
        output_path = os.path.join(output_dir, output_filename)
        woo_df.to_csv(output_path, index=False, encoding='utf-8-sig')

        logger.info(f"Successfully processed and saved to: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return None


if __name__ == "__main__":
    # 测试用例
    input_file = r"D:\PythonProject\amazon-test\scraper_excel\apple_products_20250218_164318.csv"
    output_directory = "output_excel"
    result = process_excel(input_file, output_directory)
    if result:
        print(f"Processing completed. Output file: {result}")
    else:
        print("Processing failed.")