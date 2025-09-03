import json
import os
import glob


def save_dict_to_json(
    data_dict, file_path, indent=2, ensure_ascii=False, sort_keys=False
):
    """
    将字典数据保存为JSON文件

    Args:
        data_dict (dict): 要保存的字典数据
        file_path (str): JSON文件保存路径
        indent (int, optional): 缩进空格数，默认为2，使输出更易读
        ensure_ascii (bool, optional): 是否确保ASCII编码，默认为False，支持中文等非ASCII字符
        sort_keys (bool, optional): 是否按键排序，默认为False

    Returns:
        bool: 保存是否成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        # 使用json.dump直接将字典写入文件
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                data_dict,
                f,
                ensure_ascii=ensure_ascii,
                indent=indent,
                sort_keys=sort_keys,
            )

        print(f"JSON数据已成功保存到: {file_path}")
        return True
    except Exception as e:
        print(f"保存JSON数据时出错: {e}")
        return False


def save_str_to_json(json_str, file_path):
    """
    将JSON字符串保存为JSON文件

    Args:
        json_str (str): JSON格式的字符串
        file_path (str): JSON文件保存路径

    Returns:
        bool: 保存是否成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        # 先验证JSON字符串是否有效
        json.loads(json_str)

        # 写入文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json_str)

        print(f"JSON字符串已成功保存到: {file_path}")
        return True
    except json.JSONDecodeError:
        print("提供的字符串不是有效的JSON格式")
        return False
    except Exception as e:
        print(f"保存JSON字符串时出错: {e}")
        return False


def load_json_from_file(file_path):
    """
    从JSON文件中加载数据（作为参考）

    Args:
        file_path (str): JSON文件路径

    Returns:
        dict: 加载的字典数据，若失败则返回None
    """
    try:
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data
    except Exception as e:
        print(f"加载JSON文件时出错: {e}")
        return None


def get_all_json_files(directory_path, recursive=True, include_hidden=False):
    """
    获取指定目录及其子目录中所有JSON文件的路径

    Args:
        directory_path (str): 要搜索的目录路径
        recursive (bool, optional): 是否递归搜索子目录，默认为True
        include_hidden (bool, optional): 是否包含隐藏文件（以.开头的文件），默认为False

    Returns:
        list: 所有找到的JSON文件的绝对路径列表
    """
    json_files = []

    # 确保目录存在
    if not os.path.exists(directory_path):
        print(f"目录不存在: {directory_path}")
        return json_files

    if not os.path.isdir(directory_path):
        print(f"指定路径不是目录: {directory_path}")
        return json_files

    # 转换为绝对路径
    directory_path = os.path.abspath(directory_path)

    if recursive:
        # 递归搜索所有子目录
        for root, dirs, files in os.walk(directory_path):
            for file in files:  # type: str
                file: str
                # 检查文件扩展名是否为.json
                if file.lower().endswith(".json"):
                    # 检查是否包含隐藏文件
                    if not include_hidden and file.startswith("."):
                        continue

                    # 构建完整文件路径
                    full_path = os.path.join(root, file)
                    json_files.append(full_path)
    else:
        # 只搜索当前目录
        search_pattern = os.path.join(directory_path, "*.json")
        json_files = glob.glob(search_pattern)

        # 过滤隐藏文件（如果需要）
        if not include_hidden:
            json_files = [
                f for f in json_files if not os.path.basename(f).startswith(".")
            ]

    return json_files


# 示例使用
if __name__ == "__main__":
    # 示例数据，包含中文
    example_data = {
        "name": "测试项目",
        "version": "1.0.0",
        "settings": {"debug": True, "timeout": 30, "max_connections": 100},
        "users": [
            {"id": 1, "name": "张三", "role": "admin"},
            {"id": 2, "name": "李四", "role": "user"},
        ],
        "created_at": "2023-10-01T10:00:00",
    }

    # 示例1: 直接保存字典到JSON文件
    save_dict_to_json(
        example_data,
        "../data/example_config.json",
        indent=4,  # 使用4个空格缩进
        ensure_ascii=False,  # 支持中文
        sort_keys=True,  # 按键排序
    )

    # 示例2: 先转为JSON字符串，再保存
    json_string = json.dumps(example_data, ensure_ascii=False, indent=2)
    save_str_to_json(json_string, "../data/example_config_str.json")

    # 示例3: 加载保存的JSON文件（验证保存是否成功）
    loaded_data = load_json_from_file("../data/example_config.json")
    if loaded_data:
        print("\n加载的JSON数据:")
        print(json.dumps(loaded_data, ensure_ascii=False, indent=2))

    # 示例4: 获取指定目录及其子目录中所有JSON文件
    json_files = get_all_json_files("../data")
    print("\n找到的JSON文件:")
    for file in json_files:
        print(f"- {file}")
