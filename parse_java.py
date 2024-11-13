import javalang
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class FieldType(Enum):
    PRIMITIVE = "primitive"
    COLLECTION = "collection"
    MAP = "map"
    CUSTOM = "custom"
    ENUM = "enum"


@dataclass
class GenericInfo:
    raw_type: str
    type_arguments: List[Any]  # 可以是字符串或者GenericInfo

    def to_dict(self) -> Dict[str, Any]:
        return {
            'rawType': self.raw_type,
            'typeArguments': [
                arg.to_dict() if isinstance(arg, GenericInfo) else arg
                for arg in self.type_arguments
            ]
        }


@dataclass
class EnumConstant:
    name: str
    arguments: List[str]


@dataclass
class EnumInfo:
    name: str
    constants: List[EnumConstant]
    annotations: List[Dict[str, Any]]
    modifiers: List[str]


@dataclass
class FieldInfo:
    name: str
    type: str
    field_type: FieldType
    modifiers: List[str]
    generic_info: Optional[GenericInfo] = None
    annotations: List[Dict[str, Any]] = None
    is_array: bool = False

    def __post_init__(self):
        if self.annotations is None:
            self.annotations = []


@dataclass
class ClassInfo:
    name: str
    modifiers: List[str]
    fields: List[FieldInfo]
    annotations: List[Dict[str, Any]]
    extends: Optional[str] = None
    implements: List[str] = None

    def __post_init__(self):
        if self.implements is None:
            self.implements = []


class JavaEntityParser:
    PRIMITIVE_TYPES = {
        'byte', 'short', 'int', 'long', 'float', 'double', 'boolean', 'char',
        'Byte', 'Short', 'Integer', 'Long', 'Float', 'Double', 'Boolean', 'Character',
        'String', 'BigDecimal', 'BigInteger', 'Date', 'LocalDate', 'LocalDateTime'
    }

    COLLECTION_TYPES = {'List', 'Set', 'Collection', 'ArrayList', 'HashSet', 'LinkedList', 'TreeSet'}
    MAP_TYPES = {'Map', 'HashMap', 'TreeMap', 'LinkedHashMap', 'ConcurrentHashMap'}

    def __init__(self, java_code: str):
        self.java_code = java_code
        try:
            self.tree = javalang.parse.parse(java_code)
        except Exception as e:
            raise ValueError(f"Failed to parse Java code: {str(e)}")
        self.classes: List[ClassInfo] = []
        self.enums: List[EnumInfo] = []
        self.parse()

    def _parse_annotations(self, node) -> List[Dict[str, Any]]:
        """解析注解信息"""
        annotations = []
        if hasattr(node, 'annotations'):
            for ann in node.annotations:
                annotation = {
                    'name': ann.name,
                    'parameters': {}
                }
                if ann.element is not None and hasattr(ann.element, 'pairs'):
                    for pair in ann.element.pairs:
                        if hasattr(pair.value, 'value'):
                            value = pair.value.value
                        elif hasattr(pair.value, 'members'):
                            value = [m.value for m in pair.value.members]
                        else:
                            value = str(pair.value)
                        annotation['parameters'][pair.name] = value
                annotations.append(annotation)
        return annotations

    def _parse_generic_type(self, type_node) -> Optional[GenericInfo]:
        """递归解析泛型类型"""
        if not hasattr(type_node, 'arguments') or not type_node.arguments:
            return None

        type_arguments = []
        for arg in type_node.arguments:
            if hasattr(arg, 'type'):
                # 如果类型参数本身也是泛型类型
                if hasattr(arg.type, 'arguments') and arg.type.arguments:
                    nested_generic = self._parse_generic_type(arg.type)
                    if nested_generic:
                        type_arguments.append(nested_generic)
                else:
                    type_arguments.append(arg.type.name if hasattr(arg.type, 'name') else str(arg.type))

        return GenericInfo(
            raw_type=type_node.name,
            type_arguments=type_arguments
        )

    def _parse_type(self, type_node) -> tuple[str, FieldType, Optional[GenericInfo]]:
        """解析类型信息"""
        base_type = str(type_node)
        is_array = False

        # 处理数组类型
        if hasattr(type_node, 'dimensions') and type_node.dimensions:
            is_array = True
            # 如果是ReferenceType，需要从name属性获取基础类型
            if hasattr(type_node, 'name'):
                base_type = type_node.name
            # 如果是BasicType，直接使用其值
            elif isinstance(type_node, javalang.tree.BasicType):
                base_type = type_node.name
        elif hasattr(type_node, 'name'):
            base_type = type_node.name

        # 确定字段类型
        if base_type in self.PRIMITIVE_TYPES:
            field_type = FieldType.PRIMITIVE
            generic_info = None
        elif base_type in self.COLLECTION_TYPES:
            field_type = FieldType.COLLECTION
            generic_info = self._parse_generic_type(type_node)
        elif base_type in self.MAP_TYPES:
            field_type = FieldType.MAP
            generic_info = self._parse_generic_type(type_node)
        else:
            # 检查是否为枚举类型
            is_enum = self._is_enum_type(base_type)
            field_type = FieldType.ENUM if is_enum else FieldType.CUSTOM
            generic_info = self._parse_generic_type(type_node)

        return base_type, field_type, generic_info, is_array  # 注意这里添加了is_array的返回

    def _parse_enum_constants(self, enum_node) -> List[EnumConstant]:
        """解析枚举常量"""
        constants = []
        for constant in enum_node.body.constants:
            arguments = []
            if constant.arguments:
                for arg in constant.arguments:
                    if hasattr(arg, 'value'):
                        arguments.append(str(arg.value))
                    else:
                        arguments.append(str(arg))
            constants.append(EnumConstant(
                name=constant.name,
                arguments=arguments
            ))
        return constants

    def _parse_field(self, field_node) -> List[FieldInfo]:
        """解析字段信息"""
        fields = []
        type_node = field_node.type
        base_type, field_type, generic_info, is_array = self._parse_type(type_node)

        # 解析每个声明符
        for declarator in field_node.declarators:
            field_info = FieldInfo(
                name=declarator.name,
                type=base_type,
                field_type=field_type,
                modifiers=list(field_node.modifiers),
                generic_info=generic_info,
                annotations=self._parse_annotations(field_node),
                is_array=is_array  # 使用解析出的is_array值
            )
            fields.append(field_info)

        return fields

    def _is_enum_type(self, type_name: str) -> bool:
        """检查是否为枚举类型"""
        for path, node in self.tree.filter(javalang.tree.EnumDeclaration):
            if node.name == type_name:
                return True
        return False

    def parse(self):
        """解析Java代码"""
        self.classes.clear()
        self.enums.clear()

        # 解析枚举类型
        for path, node in self.tree.filter(javalang.tree.EnumDeclaration):
            enum_info = EnumInfo(
                name=node.name,
                constants=self._parse_enum_constants(node),
                annotations=self._parse_annotations(node),
                modifiers=list(node.modifiers)
            )
            self.enums.append(enum_info)

        # 解析类
        for path, node in self.tree.filter(javalang.tree.ClassDeclaration):
            fields = []
            for field in node.fields:
                fields.extend(self._parse_field(field))

            class_info = ClassInfo(
                name=node.name,
                modifiers=list(node.modifiers),
                fields=fields,
                annotations=self._parse_annotations(node),
                extends=node.extends.name if node.extends else None,
                implements=[impl.name for impl in node.implements] if node.implements else []
            )
            self.classes.append(class_info)

    def get_parsed_info(self) -> Dict[str, Any]:
        """获取解析结果"""
        result = {
            "classes": [],
            "enums": []
        }

        # 添加类信息
        for class_info in self.classes:
            class_dict = {
                'name': class_info.name,
                'modifiers': class_info.modifiers,
                'annotations': class_info.annotations,
                'extends': class_info.extends,
                'implements': class_info.implements,
                'fields': []
            }

            for field in class_info.fields:
                field_dict = {
                    'name': field.name,
                    'type': field.type,
                    'fieldType': field.field_type.value,
                    'modifiers': field.modifiers,
                    'annotations': field.annotations,
                    'isArray': field.is_array
                }

                if field.generic_info:
                    field_dict['genericInfo'] = field.generic_info.to_dict()

                class_dict['fields'].append(field_dict)

            result['classes'].append(class_dict)

        # 添加枚举信息
        for enum_info in self.enums:
            enum_dict = {
                'name': enum_info.name,
                'modifiers': enum_info.modifiers,
                'annotations': enum_info.annotations,
                'constants': [
                    {
                        'name': constant.name,
                        'arguments': constant.arguments
                    }
                    for constant in enum_info.constants
                ]
            }
            result['enums'].append(enum_dict)

        return result


# 测试代码
if __name__ == "__main__":
    test_code = """
    @Entity
    public class Order {
        @Id
        private Long id;

        private Map<String, List<OrderItem>> itemsByCategory;

        private OrderStatus status;

        @OneToMany
        private List<OrderItem> items;
    }

    public class OrderItem {
        private Long id;
        private String name;
        private BigDecimal price;
    }

    @JsonFormat
    public enum OrderStatus {
        PENDING("P", "待处理"),
        PROCESSING("R", "处理中"),
        COMPLETED("C", "已完成"),
        CANCELLED("X", "已取消");

        private final String code;
        private final String description;

        OrderStatus(String code, String description) {
            this.code = code;
            this.description = description;
        }
    }
    """

    parser = JavaEntityParser(test_code)
    import json

    print(json.dumps(parser.get_parsed_info(), indent=2))