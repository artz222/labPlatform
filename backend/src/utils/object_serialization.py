import pickle
import json
import shelve
import os
from typing import Any, Dict, List, Optional, TypeVar


T = TypeVar('T')


def save_with_pickle(obj: Any, file_path: str) -> bool:
    """
    使用pickle将Python对象序列化并保存到文件
    
    Args:
        obj: 要序列化的Python对象
        file_path: 保存文件的路径
        
    Returns:
        bool: 保存是否成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            pickle.dump(obj, f)
        
        print(f"对象已成功使用pickle保存到: {file_path}")
        return True
    except Exception as e:
        print(f"使用pickle保存对象时出错: {e}")
        return False


def load_with_pickle(file_path: str) -> Optional[Any]:
    """
    从pickle文件中加载序列化的Python对象
    
    Args:
        file_path: 包含序列化对象的文件路径
        
    Returns:
        Any: 反序列化后的Python对象，如果失败则返回None
    """
    try:
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return None
        
        with open(file_path, 'rb') as f:
            obj = pickle.load(f)
        
        return obj
    except Exception as e:
        print(f"从pickle文件加载对象时出错: {e}")
        return None


def save_with_json(obj: Any, file_path: str, indent: int = 2, ensure_ascii: bool = False) -> bool:
    """
    使用json将Python对象序列化并保存到文件（仅支持JSON可序列化的对象）
    
    Args:
        obj: 要序列化的Python对象（必须是JSON可序列化的）
        file_path: 保存文件的路径
        indent: 缩进空格数，默认为2
        ensure_ascii: 是否确保ASCII编码，默认为False（支持中文等非ASCII字符）
        
    Returns:
        bool: 保存是否成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # 尝试将对象转换为JSON可序列化的格式
        def make_serializable(obj):
            if hasattr(obj, '__dict__'):
                # 处理自定义类实例
                result = obj.__dict__.copy()
                # 添加类名信息，便于反序列化时识别
                result['__class__'] = obj.__class__.__name__
                return result
            elif isinstance(obj, (list, tuple)):
                # 处理列表和元组
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, dict):
                # 处理字典
                return {key: make_serializable(value) for key, value in obj.items()}
            else:
                # 基本类型直接返回
                return obj
        
        serializable_obj = make_serializable(obj)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_obj, f, ensure_ascii=ensure_ascii, indent=indent)
        
        print(f"对象已成功使用json保存到: {file_path}")
        return True
    except (TypeError, OverflowError) as e:
        print(f"对象不可JSON序列化: {e}")
        return False
    except Exception as e:
        print(f"使用json保存对象时出错: {e}")
        return False


def load_with_json(file_path: str) -> Optional[Dict]:
    """
    从json文件中加载序列化的Python对象
    
    Args:
        file_path: 包含序列化对象的文件路径
        
    Returns:
        Dict: 反序列化后的字典对象，如果失败则返回None
    """
    try:
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    except Exception as e:
        print(f"从json文件加载对象时出错: {e}")
        return None


def save_with_shelve(obj_dict: Dict[str, Any], file_path: str) -> bool:
    """
    使用shelve将Python对象字典序列化并保存到文件
    
    Args:
        obj_dict: 键值对字典，其中值是要序列化的Python对象
        file_path: 保存文件的路径（不包括扩展名，shelve会自动添加）
        
    Returns:
        bool: 保存是否成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with shelve.open(file_path) as db:
            for key, value in obj_dict.items():
                db[key] = value
        
        print(f"对象字典已成功使用shelve保存到: {file_path}")
        return True
    except Exception as e:
        print(f"使用shelve保存对象时出错: {e}")
        return False


def load_with_shelve(file_path: str) -> Optional[Dict[str, Any]]:
    """
    从shelve文件中加载序列化的Python对象字典
    
    Args:
        file_path: 包含序列化对象的文件路径（不包括扩展名）
        
    Returns:
        Dict[str, Any]: 包含所有反序列化对象的字典，如果失败则返回None
    """
    try:
        result = {}
        
        try:
            with shelve.open(file_path) as db:
                for key in db:
                    result[key] = db[key]
        except Exception as e:
            # 尝试添加扩展名
            extended_path = file_path + '.dat'
            if os.path.exists(extended_path):
                with shelve.open(file_path) as db:
                    for key in db:
                        result[key] = db[key]
            else:
                print(f"shelve文件不存在: {file_path}")
                return None
        
        return result
    except Exception as e:
        print(f"从shelve文件加载对象时出错: {e}")
        return None


def serialize_to_file(
    obj: Any, 
    file_path: str, 
    method: str = 'pickle', 
    **kwargs
) -> bool:
    """
    统一的对象序列化接口，根据指定的方法将对象保存到文件
    
    Args:
        obj: 要序列化的Python对象
        file_path: 保存文件的路径
        method: 序列化方法，可选值: 'pickle', 'json', 'shelve'
        **kwargs: 传递给具体序列化方法的额外参数
        
    Returns:
        bool: 保存是否成功
    """
    method = method.lower()
    
    if method == 'pickle':
        return save_with_pickle(obj, file_path)
    elif method == 'json':
        indent = kwargs.get('indent', 2)
        ensure_ascii = kwargs.get('ensure_ascii', False)
        return save_with_json(obj, file_path, indent=indent, ensure_ascii=ensure_ascii)
    elif method == 'shelve':
        # 对于shelve，确保obj是字典
        if not isinstance(obj, dict):
            obj = {'__main_object__': obj}
        return save_with_shelve(obj, file_path)
    else:
        print(f"不支持的序列化方法: {method}")
        return False


def deserialize_from_file(
    file_path: str, 
    method: str = 'pickle'
) -> Optional[Any]:
    """
    统一的对象反序列化接口，根据指定的方法从文件加载对象
    
    Args:
        file_path: 包含序列化对象的文件路径
        method: 反序列化方法，可选值: 'pickle', 'json', 'shelve'
        
    Returns:
        Any: 反序列化后的Python对象，如果失败则返回None
    """
    method = method.lower()
    
    if method == 'pickle':
        return load_with_pickle(file_path)
    elif method == 'json':
        return load_with_json(file_path)
    elif method == 'shelve':
        result = load_with_shelve(file_path)
        # 如果是通过shelve的统一接口保存的单个对象，返回该对象
        if result and '__main_object__' in result:
            return result['__main_object__']
        return result
    else:
        print(f"不支持的反序列化方法: {method}")
        return None


# 示例用法
if __name__ == "__main__":
    # 定义一些示例类
    class Person:
        def __init__(self, name, age, city):
            self.name = name
            self.age = age
            self.city = city
            
        def __str__(self):
            return f"Person(name='{self.name}', age={self.age}, city='{self.city}')"
    
    class Student(Person):
        def __init__(self, name, age, city, student_id, major):
            super().__init__(name, age, city)
            self.student_id = student_id
            self.major = major
            self.courses = []
        
        def add_course(self, course):
            self.courses.append(course)
        
        def __str__(self):
            base_str = super().__str__()
            return f"Student({{{base_str[7:-1]}, student_id='{self.student_id}', major='{self.major}', courses={self.courses}}})"
    
    # 创建示例对象
    alice = Person("Alice", 25, "北京")
    bob = Student("Bob", 22, "上海", "20230001", "计算机科学")
    bob.add_course("Python编程")
    bob.add_course("数据结构")
    
    # 测试pickle序列化
    print("\n=== 测试pickle序列化 ===")
    pickle_file = "../data/person_data.pkl"
    save_with_pickle([alice, bob], pickle_file)
    loaded_objects = load_with_pickle(pickle_file)
    if loaded_objects:
        print("加载的对象:")
        for obj in loaded_objects:
            print(f"  - {obj}")
    
    # 测试json序列化
    print("\n=== 测试json序列化 ===")
    json_file = "../data/person_data.json"
    save_with_json([alice, bob], json_file)
    loaded_data = load_with_json(json_file)
    if loaded_data:
        print("加载的JSON数据:")
        print(json.dumps(loaded_data, ensure_ascii=False, indent=2))
    
    # 测试shelve序列化
    print("\n=== 测试shelve序列化 ===")
    shelve_file = "../data/person_db"
    save_with_shelve({"alice": alice, "bob": bob}, shelve_file)
    loaded_db = load_with_shelve(shelve_file)
    if loaded_db:
        print("加载的数据库对象:")
        for key, obj in loaded_db.items():
            print(f"  {key}: {obj}")
    
    # 测试统一接口
    print("\n=== 测试统一接口 ===")
    # 使用pickle
    serialize_to_file([alice, bob], "../data/unified_pickle.pkl", method="pickle")
    loaded = deserialize_from_file("../data/unified_pickle.pkl", method="pickle")
    print(f"通过统一接口加载pickle对象: {[str(obj) for obj in loaded] if loaded else '失败'}")
    
    # 使用json
    serialize_to_file([alice, bob], "../data/unified_json.json", method="json", indent=4)
    loaded = deserialize_from_file("../data/unified_json.json", method="json")
    print(f"通过统一接口加载json对象: {'成功' if loaded else '失败'}")
    
    # 使用shelve
    serialize_to_file({"alice": alice, "bob": bob}, "../data/unified_shelve", method="shelve")
    loaded = deserialize_from_file("../data/unified_shelve", method="shelve")
    print(f"通过统一接口加载shelve对象: {'成功' if loaded else '失败'}")