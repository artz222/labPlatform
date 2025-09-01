import csv
from typing import List, Dict


def dict_to_csv(data: List[Dict], filename: str, fieldnames=None):
    """
    将字典列表转换为CSV文件

    参数:
        data: 字典列表，每个字典表示一行数据
        filename: 输出的CSV文件名
        fieldnames: CSV文件的列名，如果为None则从第一个字典中提取
    """
    if not data:
        print("数据为空，无法生成CSV文件")
        return

    # 如果没有指定列名，则从第一个字典中提取
    if not fieldnames:
        fieldnames = data[0].keys()

    try:
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # 写入表头
            writer.writeheader()

            # 写入数据行
            for row in data:
                writer.writerow(row)

        print(f"CSV文件 '{filename}' 已成功生成")
    except Exception as e:
        print(f"生成CSV文件时出错: {e}")


# 示例用法
if __name__ == "__main__":
    # 示例1: 简单字典列表
    data1 = [
        {"姓名": "张三", "年龄": 25, "城市": "北京"},
        {"姓名": "李四", "年龄": 30, "城市": "上海"},
        {"姓名": "王五", "年龄": 35, "城市": "广州"},
    ]
    dict_to_csv(data1, "example1.csv")

    # 示例2: 指定列名顺序
    data2 = [
        {"id": 1, "name": "Alice", "score": 95},
        {"id": 2, "name": "Bob", "score": 88},
        {"id": 3, "name": "Charlie", "score": 92},
    ]
    dict_to_csv(data2, "example2.csv", fieldnames=["id", "name", "score"])

    # 示例3: 处理缺失值
    data3 = [
        {"product": "手机", "price": 3999, "stock": 100},
        {"product": "电脑", "price": 5999},
        {"product": "平板", "stock": 50},
    ]
    dict_to_csv(data3, "example3.csv")
