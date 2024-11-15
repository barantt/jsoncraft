import streamlit as st
import json
from typing import Dict, Any
import pyperclip
from parse_java import JavaEntityParser  # 假设我们之前的解析器代码保存在 java_parser.py
from generate_json import JsonGenerator  # 假设我们之前的生成器代码保存在 json_generator.py

# 设置页面配置
st.set_page_config(
    page_title="JsonCraft",
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
@Entity
public class User {
    @Id
    private Long id;

    @NotNull
    private String username;

    private String[] tags;

    @Email
    private String email;

    private UserType userType;

    private List<Order> orders;

    private Map<String, List<Product>> productsByCategory;

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


def main():
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
        tab1, tab2 = st.tabs(["JSON 示例", "解析信息"])

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
                # 显示类信息
                st.write("📚 已解析的类：")
                for class_info in st.session_state.parsed_info["classes"]:
                    with st.expander(f"类：{class_info['name']}", expanded=True):
                        st.write("🏷️ 修饰符：", ", ".join(class_info["modifiers"]))
                        if class_info["extends"]:
                            st.write("👆 继承自：", class_info["extends"])
                        if class_info["implements"]:
                            st.write("🤝 实现接口：", ", ".join(class_info["implements"]))

                        st.write("📝 字段：")
                        for field in class_info["fields"]:
                            field_info = (
                                f"- {field['name']}: {field['type']}"
                                f"{' (数组)' if field.get('isArray') else ''}"
                            )
                            if "genericInfo" in field:
                                generic = field["genericInfo"]
                                field_info += f" <{', '.join(str(arg) for arg in generic['typeArguments'])}>"
                            st.write(field_info)

                # 显示枚举信息
                if st.session_state.parsed_info["enums"]:
                    st.write("🔢 已解析的枚举：")
                    for enum_info in st.session_state.parsed_info["enums"]:
                        with st.expander(f"枚举：{enum_info['name']}", expanded=True):
                            st.write("🏷️ 修饰符：", ", ".join(enum_info["modifiers"]))
                            st.write("📝 常量：")
                            for constant in enum_info["constants"]:
                                const_info = f"- {constant['name']}"
                                if constant["arguments"]:
                                    const_info += f" ({', '.join(constant['arguments'])})"
                                st.write(const_info)

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
