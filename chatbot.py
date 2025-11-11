import streamlit as st
import openai  # 保留基础导入，兼容旧版本
import time

# 兼容处理：检查OpenAI库版本，自动适配新旧语法
try:
    from openai import OpenAI  # 新版本语法（v1.x+）
    NEW_API = True
except ImportError:
    # 旧版本语法（v0.28及以下）
    NEW_API = False

# 页面配置
st.set_page_config(
    page_title="Role-based Creative Chatbot",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
.reportview-container { background-color: #f9fafb; }
.main .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px; }
.stTitle { color: #1e293b; font-weight: 700; margin-bottom: 0.5rem !important; }
.stCaption { color: #64748b; font-size: 1.1rem; margin-bottom: 1.5rem !important; }
.role-card { background: white; border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05); transition: transform 0.2s; }
.role-card:hover { transform: translateY(-3px); }
.stChatMessage { border-radius: 18px; margin-bottom: 1rem; }
.stChatMessage > div:first-child { border-radius: 50%; width: 40px; height: 40px; }
.stTextInput > div > div > input { border-radius: 20px; padding: 0.75rem 1.25rem; border: 1px solid #e2e8f0; }
.sidebar-content { background-color: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.sidebar-header { color: #1e293b; font-size: 1.3rem; font-weight: 600; margin-bottom: 1.5rem; padding-bottom: 0.5rem; border-bottom: 2px solid #eff6ff; }
</style>
""", unsafe_allow_html=True)

# 角色配置（带头像和简介）
ROLES = {
    "Film Director": {
        "prompt": """You are an award-winning film director with 20 years of experience. Expert in cinematography and narrative pacing. Speak with authority but warmth.""",
        "avatar": "🎬",
        "bio": "Award-winning director specializing in visual storytelling."
    },
    "Sci-Fi Writer": {
        "prompt": """You are a Hugo Award-nominated sci-fi author, master of worldbuilding. Blend scientific accuracy with compelling storytelling.""",
        "avatar": "🚀",
        "bio": "Hard sci-fi author focusing on futuristic societies."
    },
    "Street Artist": {
        "prompt": """You are a globally recognized street artist. Blend social commentary with bold visuals. Use urban slang naturally.""",
        "avatar": "🎨",
        "bio": "Rebellious muralist merging social messages with urban art."
    },
    "Electronic Music Producer": {
        "prompt": """You are a platinum-selling EDM producer. Explain production techniques in accessible terms. Share studio tips.""",
        "avatar": "🎧",
        "bio": "Producer specializing in electronic sound design."
    },
    "Game Designer": {
        "prompt": """You are a lead designer of top-selling indie games. Expert in gameplay-mechanic storytelling. Provide concrete design ideas.""",
        "avatar": "🎮",
        "bio": "Indie game designer merging gameplay with storytelling."
    }
}

# 初始化会话状态
if "selected_role" not in st.session_state:
    st.session_state.selected_role = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "first_visit" not in st.session_state:
    st.session_state.first_visit = True
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# 侧边栏配置
with st.sidebar:
    st.markdown('<div class="sidebar-header">🎭 Role Configuration</div>', unsafe_allow_html=True)
    
    # API Key输入
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        key="api_key_input",
        placeholder="sk-proj-...",
        help="Get your key from https://platform.openai.com/api-keys",
        value=st.session_state.api_key
    )
    st.session_state.api_key = api_key
    
    st.divider()
    
    # 角色选择
    st.markdown("**Select a Creative Expert**", unsafe_allow_html=True)
    selected_role = st.selectbox(
        "Choose a role to chat with",
        options=list(ROLES.keys()),
        index=None,
        placeholder="Select a role...",
        key="role_select"
    )
    
    # 显示角色简介
    if selected_role:
        st.markdown(f"""
        <div class="role-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{ROLES[selected_role]['avatar']}</div>
            <div style="font-weight: 600; color: #1e293b;">{selected_role}</div>
            <div style="color: #64748b; font-size: 0.9rem;">{ROLES[selected_role]['bio']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 切换角色清空历史
    if selected_role != st.session_state.selected_role:
        st.session_state.selected_role = selected_role
        st.session_state.messages = []
        if selected_role:
            st.success(f"Switched to {selected_role} ✅")
    
    st.divider()
    
    # 使用指南
    with st.expander("📖 How to Use", expanded=False):
        st.markdown("""
        1. Enter your OpenAI API key
        2. Select a creative expert from the dropdown
        3. Type your question in the chat box
        4. Get role-specific insights
        """)

# 主页面内容
st.title("✨Role-based Creative Chatbot")
st.caption("Select a creative role and ask your question!")
st.divider()

# 首次访问提示
if st.session_state.first_visit and not st.session_state.messages:
    with st.info("👋 Welcome! Select a role from the sidebar to start chatting."):
        st.write("Examples:")
        st.code("Film Director: How to shoot an emotional dialogue scene?")
        st.code("Sci-Fi Writer: What's a unique alien social structure?")
    st.session_state.first_visit = False

# 核心聊天逻辑
if not st.session_state.api_key:
    st.warning("⚠️ Please enter your OpenAI API key in the sidebar")
elif not st.session_state.selected_role:
    st.info("ℹ️ Select a creative expert from the sidebar to begin")
else:
    # 配置API Key（兼容新旧版本）
    if NEW_API:
        client = OpenAI(api_key=st.session_state.api_key)
    else:
        openai.api_key = st.session_state.api_key
    
    # 显示聊天历史
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            with st.chat_message(msg["role"], avatar=ROLES[st.session_state.selected_role]["avatar"]):
                st.markdown(msg["content"])
        else:
            with st.chat_message(msg["role"], avatar="👤"):
                st.markdown(msg["content"])
    
    # 处理用户输入
    if prompt := st.chat_input(f"Ask {st.session_state.selected_role}..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # 生成回复（兼容新旧API）
        with st.chat_message("assistant", avatar=ROLES[st.session_state.selected_role]["avatar"]):
            with st.spinner(f"{st.session_state.selected_role} is thinking..."):
                full_messages = [
                    {"role": "system", "content": ROLES[st.session_state.selected_role]["prompt"]}
                ] + st.session_state.messages
                
                try:
                    # 流式回复（区分新旧版本API）
                    if NEW_API:
                        # 新版本API（v1.x+）
                        stream = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=full_messages,
                            stream=True,
                            temperature=0.8
                        )
                        response = ""
                        response_placeholder = st.empty()
                        for chunk in stream:
                            if chunk.choices[0].delta.content:
                                response += chunk.choices[0].delta.content
                                response_placeholder.markdown(response + "▌")
                                time.sleep(0.02)
                        response_placeholder.markdown(response)
                    else:
                        # 旧版本API（v0.28及以下）
                        stream = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=full_messages,
                            stream=True,
                            temperature=0.8
                        )
                        response = st.write_stream(stream)
                    
                    st.session_state.messages.append({"role": "assistant", "content": response})
                
                except Exception as e:
                    error_msg = str(e)
                    if "insufficient_quota" in error_msg:
                        st.error("💸 Quota Exceeded: Add a payment method in OpenAI billing.")
                    elif "invalid_api_key" in error_msg:
                        st.error("🔑 Invalid API Key: Check your key and try again.")
                    else:
                        st.error(f"❌ Error: {error_msg}")

# 页脚
st.markdown("""
<div style="margin-top: 2rem; text-align: center; color: #94a3b8; font-size: 0.9rem;">
    Built for 'Art & Advanced Big Data' • ZHANG YUE
</div>
""", unsafe_allow_html=True)
