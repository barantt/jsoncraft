import pandas as pd
import streamlit as st
from streamlit.components.v1 import html
import json
from typing import Dict, Any, Set, List
from parse_java import JavaEntityParser  # 假设我们之前的解析器代码保存在 java_parser.py
from generate_json import JsonGenerator  # 假设我们之前的生成器代码保存在 json_generator.py

# SEO相关的HTML代码
seo_html = """
<head>
    <!-- 页面标题 -->
    <title>JsonCraft - Java实体类JSON示例生成器 | 在线工具</title>

    <!-- Meta 标签 -->
    <meta name="description" content="JsonCraft是一款专为Java开发者设计的JSON示例生成工具，支持复杂类型、泛型、注解等特性，提高开发效率。">
    <meta name="keywords" content="Java,JSON,示例生成,在线工具,实体类,Bean,JSON生成器,Spring Boot">

    <!-- Open Graph 标签 (用于社交媒体分享) -->
    <meta property="og:title" content="JsonCraft - Java实体类JSON示例生成器">
    <meta property="og:description" content="一键将Java实体类转换为JSON示例，支持复杂类型、泛型、注解等特性">
    <meta property="og:url" content="http://javatojson.cn">
    <meta property="og:type" content="website">

    <!-- Twitter Card 标签 -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="JsonCraft - Java实体类JSON示例生成器">
    <meta name="twitter:description" content="一键将Java实体类转换为JSON示例，支持复杂类型、泛型、注解等特性">

    <!-- 规范链接 -->
    <link rel="canonical" href="http://javatojson.cn">

    <!-- 结构化数据 (Schema.org) -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "JsonCraft",
        "description": "Java实体类JSON示例生成器",
        "url": "https://你的域名.com",
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "All",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        }
    }
    </script>
</head>
"""


# 注入 SEO HTML
def inject_seo():
    html(seo_html, height=0)


# 设置页面配置
st.set_page_config(
    page_title="JsonCraft - Java实体类JSON示例生成器",
    page_icon="⚒️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式
st.markdown("""
    <style>
        /* 隐藏 Streamlit 默认元素 */
        #MainMenu {visibility: hidden;}
        .stDeployButton {display: none;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* 减小顶部空白 */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }

        /* 自定义标题样式 */
        .custom-title {
            background: linear-gradient(45deg, #2E3192, #1BFFFF);
            padding: 1rem 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .custom-title h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }

        .custom-title p {
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }

        /* 美化分隔线 */
        hr {
            margin: 1rem 0;
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, #2E3192, transparent);
        }

        /* 美化代码输入框 */
        .stTextArea textarea {
            border-radius: 10px;
            border: 1px solid #ddd;
            font-family: 'Consolas', monospace;
        }

        /* 美化按钮 */
        .stButton button {
            border-radius: 20px;
            padding: 0.5rem 2rem;
            background: linear-gradient(45deg, #2E3192, #1BFFFF);
            border: none;
            color: white;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        /* 美化 JSON 展示区域 */
        .element-container div.json-data {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #ddd;
        }

        /* 美化展开面板 */
        .streamlit-expanderHeader {
            background: #f8f9fa;
            border-radius: 10px;
            border: 1px solid #ddd;
        }

        /* 标签页样式 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }

        .stTabs [data-baseweb="tab"] {
            height: 3rem;
            border-radius: 10px 10px 0 0;
        }

        /* 页脚样式 */
        .footer {
            background: linear-gradient(45deg, #2E3192, #1BFFFF);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-top: 2rem;
        }

        /* 调整页面整体内边距 */
        .appview-container {
            padding: 1rem 1rem 0 1rem;
        }

    </style>

    <div class="custom-title">
        <h1>JsonCraft ⚒️</h1>
        <p>Turning Java Entities into Perfect JSON, Effortlessly</p>
    </div>
""", unsafe_allow_html=True)


def create_example_code() -> str:
    return """
public class User {
    private Long id;

    private String username;

    private String[] tags;

    private String email;

    private UserType userType;

    private Product product;
    
    private List<Order> orders;

    private LocalDateTime createTime;
}

public class Order {
    private Long id;
    private String orderNo;
    private BigDecimal amount;
    private OrderStatus status;
}

public class Product {
    private Long id;
    private String name;
    private BigDecimal price;
    private Integer stock;
}

public enum OrderStatus {
    PENDING("P", "待处理"),
    PROCESSING("R", "处理中"),
    COMPLETED("C", "已完成"),
    CANCELLED("X", "已取消");

    private final String code;
    private final String description;
}

public enum UserType {
    ADMIN,
    USER,
    GUEST
}
"""


def format_json(json_str: str) -> str:
    """格式化 JSON 字符串"""
    try:
        parsed = json.loads(json_str)
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        return json_str


def parse_and_generate(java_code: str) -> tuple[bool, Dict[str, Any], str]:
    """解析 Java 代码并生成 JSON 示例"""
    try:
        # 解析 Java 代码
        parser = JavaEntityParser(java_code)
        parsed_info = parser.get_parsed_info()

        # 生成 JSON 示例
        generator = JsonGenerator(parsed_info)
        json_example = generator.to_json(indent=2)

        return True, parsed_info, json_example
    except Exception as e:
        return False, {}, str(e)


class ParameterAnalyzer:
    def __init__(self, parsed_info: Dict[str, Any]):
        self.parsed_info = parsed_info
        self.processed_types: Set[str] = set()

    def find_class_info(self, class_name: str) -> Dict[str, Any]:
        """查找类信息"""
        for cls in self.parsed_info["classes"]:
            if cls["name"] == class_name:
                return cls
        return None

    def get_field_type_display(self, field: Dict[str, Any]) -> str:
        """获取字段类型的显示字符串"""
        type_desc = field["type"]
        if field.get("genericInfo"):
            generic = field["genericInfo"]
            type_args = generic["typeArguments"]
            if isinstance(type_args, list):
                args_str = ", ".join(str(arg) if isinstance(arg, str)
                                     else f"{arg['rawType']}<{', '.join(arg['typeArguments'])}>"
                                     for arg in type_args)
                type_desc = f"{generic['rawType']}<{args_str}>"
        if field.get("isArray"):
            type_desc += "[]"
        return type_desc

    def is_complex_type(self, type_name: str) -> bool:
        """判断是否为复杂类型"""
        base_type = type_name.split("<")[0].strip("[]")
        return (
                base_type not in {
            "String", "Integer", "int", "Long", "long", "Double", "double",
            "Float", "float", "Boolean", "boolean", "Date", "LocalDate",
            "LocalDateTime", "BigDecimal", "byte", "short", "char"
        } and not any(enum["name"] == base_type for enum in self.parsed_info["enums"])
        )

    def build_parameter_list(self, class_info: Dict[str, Any], indent_level: int = 0,
                             parent_field: str = "", processed_types: Set[str] = None) -> List[Dict[str, Any]]:
        """构建带缩进的参数列表"""
        if processed_types is None:
            processed_types = set()

        result = []
        indent = "    " * indent_level
        class_name = class_info["name"]

        # 防止循环引用
        if class_name in processed_types:
            return result
        processed_types.add(class_name)

        for field in class_info["fields"]:
            field_name = f"{parent_field}.{field['name']}" if parent_field else field['name']
            type_desc = self.get_field_type_display(field)

            # 添加当前字段
            result.append({
                "字段名": indent + field_name,
                "类型": type_desc,
                "是否必填": "N",
                "备注": field_name
            })

            # 处理泛型中的复杂类型
            if field.get("genericInfo"):
                generic = field["genericInfo"]
                for type_arg in generic["typeArguments"]:
                    if isinstance(type_arg, dict):
                        nested_type = type_arg["rawType"]
                    elif isinstance(type_arg, str):
                        nested_type = type_arg
                    else:
                        continue

                    if self.is_complex_type(nested_type):
                        nested_class = self.find_class_info(nested_type)
                        if nested_class and nested_type not in processed_types:
                            result.extend(self.build_parameter_list(
                                nested_class,
                                indent_level + 1,
                                field_name,
                                processed_types
                            ))

            # 处理基本类型
            base_type = field["type"]
            if self.is_complex_type(base_type):
                nested_class = self.find_class_info(base_type)
                if nested_class and base_type not in processed_types:
                    result.extend(self.build_parameter_list(
                        nested_class,
                        indent_level + 1,
                        field_name,
                        processed_types
                    ))

        processed_types.remove(class_name)
        return result


def show_parameter_list(parsed_info: Dict[str, Any]):
    """显示参数列表"""
    if not parsed_info["classes"]:
        st.warning("未检测到类信息，请先输入Java代码")
        return

    analyzer = ParameterAnalyzer(parsed_info)

    # 类选择器
    selected_class = [cls["name"] for cls in parsed_info["classes"]][0]

    # 显示类的基本信息
    class_info = analyzer.find_class_info(selected_class)
    if class_info:
        # 构建参数列表
        parameters = analyzer.build_parameter_list(class_info)
        if parameters:
            df = pd.DataFrame(parameters)

            # 使用 Streamlit 的表格组件显示
            st.dataframe(
                df,
                column_config={
                    "字段名": st.column_config.TextColumn(
                        "字段名",
                        help="字段的完整路径",
                        width="medium"
                    ),
                    "类型": st.column_config.TextColumn(
                        "类型",
                        help="字段的类型",
                        width="medium"
                    ),
                    "是否必填": st.column_config.TextColumn(
                        "是否必填",
                        help="是否必填",
                        width="small"
                    ),
                    "备注": st.column_config.TextColumn(
                        "备注",
                        help="备注",
                        width="medium"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("该类没有字段")


def main():
    inject_seo()

    # 创建两列布局
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("### 💻 Java 代码输入")
        # 添加示例代码按钮
        if st.button("加载示例代码"):
            java_code = create_example_code()
        else:
            java_code = st.session_state.get("java_code", "")

        # 代码输入区域
        java_code = st.text_area(
            "请输入 Java 实体类代码",
            value=java_code,
            height=400,
            key="java_code"
        )

        # 解析按钮
        if st.button("生成 JSON 示例", type="primary"):
            if not java_code.strip():
                st.error("请输入 Java 代码！")
                return

            success, parsed_info, json_example = parse_and_generate(java_code)

            if success:
                st.session_state.parsed_info = parsed_info
                st.session_state.json_example = json_example
                st.success("解析成功！")
            else:
                st.error(f"解析失败：{json_example}")

    with right_col:
        st.markdown("### 🔍 解析结果")

        # 创建选项卡
        tab1, tab2 = st.tabs(["JSON示例", "表格形式"])

        with tab1:
            if "json_example" in st.session_state:
                # 格式化 JSON
                formatted_json = json.dumps(
                    json.loads(st.session_state.json_example),
                    indent=4,
                    ensure_ascii=False
                )

                # 使用 st.code() 显示 JSON，自带复制功能
                st.code(formatted_json, language="json")

                # 下载按钮
                st.download_button(
                    label="下载 JSON 文件",
                    data=st.session_state.json_example,
                    file_name="example.json",
                    mime="application/json"
                )

        with tab2:
            if "parsed_info" in st.session_state:
                show_parameter_list(st.session_state.parsed_info)
    # 添加页脚
    st.markdown("---")
    st.markdown("""
            <div class="footer">
                <p style="margin: 0;">Made with ❤️ by damao</p>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                    ⭐ 支持多重嵌套泛型 | 🎯 完整枚举解析 | 🔄 数组类型支持
                </p>
            </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
