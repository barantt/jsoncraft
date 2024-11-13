import json
import random
import string
from datetime import datetime
from typing import Any, Dict, List, Optional


class JsonGenerator:
    def __init__(self, parsed_info: Dict[str, Any]):
        self.parsed_info = parsed_info
        self.enum_values = self._build_enum_values()
        self.processed_classes = set()  # 防止循环引用

    def _generate_array(self, type_name: str, size: int = 1) -> List[Any]:
        """生成数组类型的示例值"""
        return [self._generate_value_by_type(type_name) for _ in range(size)]

    def _build_enum_values(self) -> Dict[str, List[str]]:
        """构建枚举类型到枚举值的映射"""
        enum_values = {}
        for enum_info in self.parsed_info['enums']:
            enum_values[enum_info['name']] = [
                const['name'] for const in enum_info['constants']
            ]
        return enum_values

    def _generate_primitive(self, type_name: str) -> Any:
        """生成基本类型的示例值"""
        type_generators = {
            'String': lambda: ''.join(random.choices(string.ascii_letters, k=8)),
            'Integer': lambda: random.randint(1, 100),
            'int': lambda: random.randint(1, 100),
            'Long': lambda: random.randint(1000, 9999),
            'long': lambda: random.randint(1000, 9999),
            'Double': lambda: round(random.uniform(1.0, 100.0), 2),
            'double': lambda: round(random.uniform(1.0, 100.0), 2),
            'Float': lambda: round(random.uniform(1.0, 100.0), 2),
            'float': lambda: round(random.uniform(1.0, 100.0), 2),
            'Boolean': lambda: random.choice([True, False]),
            'boolean': lambda: random.choice([True, False]),
            'BigDecimal': lambda: str(round(random.uniform(1.0, 1000.0), 2)),
            'Date': lambda: datetime.now().strftime("%Y-%m-%d"),
            'LocalDate': lambda: datetime.now().strftime("%Y-%m-%d"),
            'LocalDateTime': lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'byte': lambda: random.randint(-128, 127),
            'Byte': lambda: random.randint(-128, 127),
            'short': lambda: random.randint(-32768, 32767),
            'char': lambda: random.choice(string.ascii_letters),
            'Character': lambda: random.choice(string.ascii_letters)
        }

        return type_generators.get(type_name, lambda: f"Unknown type: {type_name}")()

    def _generate_collection(self, generic_info: Dict[str, Any], size: int = 1) -> List[Any]:
        """生成集合类型的示例值"""
        result = []
        if not generic_info['typeArguments']:
            return result

        type_arg = generic_info['typeArguments'][0]
        for _ in range(size):
            if isinstance(type_arg, dict):  # 嵌套的泛型类型
                result.append(self._generate_value_by_generic_info(type_arg))
            else:  # 简单类型
                result.append(self._generate_value_by_type(type_arg))

        return result

    def _generate_map(self, generic_info: Dict[str, Any], size: int = 1) -> Dict[str, Any]:
        """生成Map类型的示例值"""
        result = {}
        if len(generic_info['typeArguments']) < 2:
            return result

        key_type = generic_info['typeArguments'][0]
        value_type = generic_info['typeArguments'][1]

        for i in range(size):
            key = (self._generate_primitive(key_type)
                   if key_type in ['String', 'Integer', 'Long']
                   else f"key{i}")

            if isinstance(value_type, dict):  # 嵌套的泛型类型
                value = self._generate_value_by_generic_info(value_type)
            else:  # 简单类型
                value = self._generate_value_by_type(value_type)

            result[str(key)] = value

        return result

    def _generate_value_by_generic_info(self, generic_info: Dict[str, Any]) -> Any:
        """根据泛型信息生成值"""
        raw_type = generic_info['rawType']

        if raw_type in ['List', 'Set', 'Collection', 'ArrayList', 'HashSet']:
            return self._generate_collection(generic_info)
        elif raw_type in ['Map', 'HashMap', 'TreeMap', 'LinkedHashMap']:
            return self._generate_map(generic_info)
        else:
            return self._generate_value_by_type(raw_type)

    def _generate_value_by_type(self, type_name: str) -> Any:
        """根据类型生成值"""
        # 处理数组类型 (检查是否以[]结尾)
        if type_name.endswith('[]'):
            base_type = type_name[:-2]
            return self._generate_array(base_type)

        # 处理基本类型
        if type_name in ['String', 'Integer', 'int', 'Long', 'long', 'Double',
                         'double', 'Float', 'float', 'Boolean', 'boolean',
                         'BigDecimal', 'Date', 'LocalDate', 'LocalDateTime', 'byte', 'Byte', 'short', 'char',
                         'Character']:
            return self._generate_primitive(type_name)

        # 处理枚举类型
        if type_name in self.enum_values:
            return random.choice(self.enum_values[type_name])

        # 处理自定义类型
        return self._generate_object(type_name)

    def _find_class_info(self, class_name: str) -> Optional[Dict[str, Any]]:
        """查找类信息"""
        for class_info in self.parsed_info['classes']:
            if class_info['name'] == class_name:
                return class_info
        return None

    def _generate_object(self, class_name: str) -> Dict[str, Any]:
        """生成自定义类型的示例值"""
        if class_name in self.processed_classes:
            return {}

        self.processed_classes.add(class_name)
        result = {}
        class_info = self._find_class_info(class_name)

        if not class_info:
            return {}

        for field in class_info['fields']:
            field_name = field['name']
            field_type = field['type']

            # 处理数组类型
            if field.get('isArray', False):
                result[field_name] = self._generate_array(field_type)
                continue

            # 处理带泛型的类型
            if 'genericInfo' in field:
                result[field_name] = self._generate_value_by_generic_info(field['genericInfo'])
                continue

            # 处理普通类型
            result[field_name] = self._generate_value_by_type(field_type)

        self.processed_classes.remove(class_name)
        return result

    def generate_example(self, class_name: Optional[str] = None) -> Dict[str, Any]:
        """生成示例JSON数据"""
        self.processed_classes.clear()

        # 如果没有指定类名，使用第一个类
        if not class_name and self.parsed_info['classes']:
            class_name = self.parsed_info['classes'][0]['name']

        if not class_name:
            return {}

        return self._generate_object(class_name)

    def to_json(self, class_name: Optional[str] = None, indent: int = 2) -> str:
        """生成格式化的JSON字符串"""
        return json.dumps(
            self.generate_example(class_name),
            indent=indent,
            ensure_ascii=False
        )
