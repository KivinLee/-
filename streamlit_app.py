import streamlit as st
import requests
import re
from functools import lru_cache
import os

# 设置页面标题和图标
st.set_page_config(
    page_title="中英文姓名转换工具",
    page_icon="🔤",
    layout="centered"
)

# 从环境变量获取 API Key，如果没有则使用默认值
API_KEY = os.getenv('API_KEY', 'sk-agbukmffvfhuflmkieduvpzyzzraawwngmjbikxonidcgyba')

def is_chinese(text):
    """检测文本是否包含中文字符"""
    return bool(re.search('[\u4e00-\u9fff]', text))

@lru_cache(maxsize=100)
def get_name_prompt(input_name, is_chinese):
    """缓存并生成提示词"""
    if is_chinese:
        return f"""请为中文名"{input_name}"创造3个合适的英文名。要求：
1. 考虑谐音和含义的关联
2. 使用常见的英文名
3. 每个名字都要解释选择原因

请按照以下格式返回（注意不要给名字加任何特殊符号）：
1. [英文名]
寓意：[选择这个名字的原因，包括与中文名的关联]

2. [英文名]
寓意：[选择这个名字的原因，包括与中文名的关联]

3. [英文名]
寓意：[选择这个名字的原因，包括与中文名的关联]"""
    else:
        return f"""请为英文名"{input_name}"创造3个富有中国文化特色的中文名。要求：
1. 遵循中国人名的格式：姓+名
2. 选用常见的中国姓氏
3. 名字发音要尽量接近原英文名
4. 每个名字都要解释其寓意

请按照以下格式返回（注意不要给名字加任何特殊符号）：
1. [中文名]
寓意：[这个名字的含义和寓意]

2. [中文名]
寓意：[这个名字的含义和寓意]

3. [中文名]
寓意：[这个名字的含义和寓意]"""

def generate_names(input_name):
    """生成名字的核心函数"""
    is_chinese_name = is_chinese(input_name)
    prompt = get_name_prompt(input_name, is_chinese_name)

    try:
        with st.spinner('正在生成名字，请稍候...'):
            response = requests.post(
                'https://api.siliconflow.cn/v1/chat/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {API_KEY}'
                },
                json={
                    'model': 'deepseek-ai/DeepSeek-V3',
                    'messages': [
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.7,
                    'max_tokens': 1000,
                    'stream': False  # 禁用流式响应以提高速度
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'], is_chinese_name
    except requests.exceptions.Timeout:
        st.error("请求超时，请稍后重试。")
        return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"API请求失败：{str(e)}")
        return None, None
    except Exception as e:
        st.error(f"生成名字时出错：{str(e)}")
        return None, None

# 添加自定义 CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 800px;
    }
    h1 {
        color: #2c3e50 !important;
        font-size: 2.5rem !important;
        margin-bottom: 1.5rem !important;
        text-align: center !important;
    }
    .name-card {
        border: 1px solid #dee2e6 !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem !important;
        margin-bottom: 0.75rem !important;
        background-color: white !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
    }
    .name-card:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
        transition: box-shadow 0.3s ease !important;
    }
    .name-title {
        font-size: 1.5rem !important;
        font-weight: bold !important;
        color: #dc3545 !important;
        margin-bottom: 0.5rem !important;
    }
    .meaning-section {
        margin-bottom: 0.5rem !important;
    }
    .meaning-content {
        color: #6c757d !important;
        line-height: 1.3 !important;
    }
    .stButton>button {
        width: 100% !important;
        background-color: #dc3545 !important;
        color: white !important;
        font-weight: bold !important;
    }
    .stButton>button:hover {
        background-color: #c82333 !important;
    }
    .info-box {
        padding: 0.5rem !important;
        border-radius: 0.5rem !important;
        background-color: #e9f7fe !important;
        border-left: 4px solid #3498db !important;
    }
    footer {
        text-align: center !important;
        margin-top: 2rem !important;
        color: #6c757d !important;
    }
</style>
""", unsafe_allow_html=True)

# 页面标题
st.title("🔤 中英文姓名转换工具")

# 添加描述
st.markdown("""
<div style="margin-bottom: 1.5rem;">
这个工具可以帮助你：
<ul>
  <li>为中文名生成匹配的英文名</li>
  <li>为英文名创造富有中国文化特色的中文名</li>
</ul>
</div>
""", unsafe_allow_html=True)

# 输入框
input_name = st.text_input("请输入姓名", placeholder="输入中文名或英文名")

# 检测输入类型并显示提示
if input_name:
    is_chinese_input = is_chinese(input_name)
    if is_chinese_input:
        st.markdown(f"""
        <div class="info-box">
        检测到中文名：<b>{input_name}</b>，将为您生成匹配的英文名
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="info-box">
        检测到英文名：<b>{input_name}</b>，将为您生成富有中国文化特色的中文名
        </div>
        """, unsafe_allow_html=True)

# 生成按钮
if st.button("生成名字"):
    if not input_name:
        st.warning("请先输入姓名")
    else:
        result, is_chinese_name = generate_names(input_name)
        
        if result:
            st.success("名字生成成功！")
            
            # 解析结果并显示
            names = result.split('\n\n')
            
            for name_block in names:
                if not name_block.strip():
                    continue
                
                lines = name_block.strip().split('\n')
                if len(lines) >= 2:
                    # 提取名字和寓意
                    name_line = lines[0]
                    name = name_line[name_line.find('.')+1:].strip()
                    meaning = '\n'.join(lines[1:])
                    
                    # 创建卡片
                    st.markdown(f"""
                    <div class="name-card">
                        <div class="name-title">{name}</div>
                        <div class="meaning-section">
                            <div class="meaning-content">{meaning}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# 添加页脚
st.markdown("""
<footer>
© 2025 中英文姓名转换工具 | 使用 DeepSeek-V3 模型提供支持
</footer>
""", unsafe_allow_html=True)
