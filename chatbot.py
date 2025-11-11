
import streamlit as st
from openai import OpenAI  # 适配最新OpenAI库
import time

# 页面配置 - 更精致的初始设置
st.set_page_config(
    page_title="RoleCraft | Creative Expert Chatbot",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 提升视觉质感（参考链接风格+增强）
st.markdown("""
<style>
/* 全局样式 */
.reportview-container {
    background-color: #f9fafb;
}
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* 标题样式 */
.stTitle {
    color: #1e293b;
    font-weight: 700;
    margin-bottom: 0.5rem !important;
}
.stCaption {
    color: #64748b;
    font-size: 1.1rem;
    margin-bottom: 1.5rem !important;
}

/* 角色卡片样式 */
.role-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: transform 0.2s;
}
.role-card:hover {
    transform: translateY(-3px);
}

/* 聊天框样式 */
.stChatMessage {
    border-radius: 18px;
    margin-bottom: 1rem;
}
.stChatMessage > div:first-child {
    border-radius: 50%;
    width: 40px;
    height: 40px;
}

/* 按钮和输入框样式 */
.stTextInput > div > div > input {
    border-radius: 20px;
    padding: 0.75rem 1.25rem;
    border: 1px solid #e2e8f0;
}
.stButton > button {
    border-radius: 20px;
    padding: 0.5rem 1.5rem;
    background-color: #3b82f6;
    color: white;
    border: none;
}
.stButton > button:hover {
    background-color: #2563eb;
}

/* 侧边栏样式 */
.sidebar-content {
    background-color: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
.sidebar-header {
    color: #1e293b;
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #eff6ff;
}
</style>
""", unsafe_allow_html=True)

# 角色配置 - 新增头像和简介（比参考链接更丰富）
ROLES = {
    "Film Director": {
        "prompt": """
        You are an award-winning film director with 20 years of experience in indie and blockbuster films. 
        Expert in cinematography (dolly shots, lighting setups, shot composition) and narrative pacing. 
        Speak with authority but warmth, like guiding a film crew on set. Provide specific, actionable advice.
        """,
        "avatar": "🎬",  # 角色专属图标
        "bio": "Award-winning director specializing in visual storytelling and emotional narratives."
    },
    "Sci-Fi Writer": {
        "prompt": """
        You are a Hugo Award-nominated sci-fi author, master of worldbuilding and hard science integration. 
        Craft vivid details (e.g., "The exoplanet's atmosphere shimmers violet due to arsenic compounds") 
        and explore technological ethics. Blend scientific accuracy with compelling storytelling.
        """,
        "avatar": "🚀",
        "bio": "Hard sci-fi author focusing on futuristic societies and cosmic mysteries."
    },
    "Street Artist": {
        "prompt": """
        You are a globally recognized street artist with murals in 15+ cities. Blend social commentary with bold visuals. 
        Use urban slang naturally ("Graffiti ain't vandalism—it's the city's heartbeat") and discuss color theory, 
        public space politics, and subcultural expression.
        """,
        "avatar": "🎨",
        "bio": "Rebellious muralist merging social messages with vibrant urban art."
    },
    "Electronic Music Producer": {
        "prompt": """
        You are a platinum-selling EDM producer (House, Techno, Lo-Fi). Explain 4/4 rhythms, sidechain compression, 
        and synth design in accessible terms. Share studio tips, gear recommendations, and creative workflows—like 
        chatting with a fellow producer in the studio.
        """,
        "avatar": "🎧",
        "bio": "Platinum-selling producer specializing in electronic sound design and production."
    },
    "Game Designer": {
        "prompt": """
        You are a lead designer of 3 top-selling indie games, expert in gameplay-mechanic storytelling. 
        Break down level design, player immersion, and interactive narrative (e.g., "Puzzles should mirror the protagonist's emotional journey"). 
        Provide concrete, implementable design ideas.
        """,
        "avatar": "🎮",
        "bio": "Indie game designer merging innovative gameplay with compelling storytelling."
    }
}

# 初始化会话状态 - 新增更多交互状态
if "selected_role" not in st.session_state:
    st.session_state.selected_role = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "first_visit" not in st.session_state:
    st.session_state.first_visit = True  # 用于显示欢迎提示
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# 侧边栏 - 重构为更丰富的配置面板
with st.sidebar:
    # 侧边栏容器（带样式）
    with st.container():
        st.markdown('<div class="sidebar-header">🎭 Role Configuration</div>', unsafe_allow_html=True)
        
        # API Key 输入（带保存功能）
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            key="api_key_input",
            placeholder="sk-proj-...",
            help="Get your key from https://platform.openai.com/api-keys",
            value=st.session_state.api_key
        )
        st.session_state.api_key = api_key  # 保存输入的Key
        
        st.divider()
        
        # 角色选择（带预览卡片）
        st.markdown("**Select a Creative Expert**", unsafe_allow_html=True)
        selected_role = st.selectbox(
            "Choose a role to chat with",
            options=list(ROLES.keys()),
            index=None,
            placeholder="Select a role...",
            key="role_select"
        )
        
        # 显示角色简介（选中角色后）
        if selected_role:
            with st.container():
                st.markdown(f"""
                <div class="role-card">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{ROLES[selected_role]['avatar']}</div>
                    <div style="font-weight: 600; color: #1e293b;">{selected_role}</div>
                    <div style="color: #64748b; font-size: 0.9rem;">{ROLES[selected_role]['bio']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # 切换角色时清空历史
        if selected_role != st.session_state.selected_role:
            st.session_state.selected_role = selected_role
            st.session_state.messages = []
            if selected_role:
                st.success(f"Switched to {selected_role} ✅")
        
        st.divider()
        
        # 使用指南（新增功能）
        with st.expander("📖 How to Use", expanded=False):
            st.markdown("""
            1. Enter your OpenAI API key
            2. Select a creative expert from the dropdown
            3. Type your question in the chat box
            4. Get role-specific insights and advice
            
            *Tip: Ask detailed questions for more valuable responses!*
            """)

# 主页面 - 增强视觉层次和交互体验
st.title("✨ RoleCraft: Creative Expert Chatbot")
st.caption("Chat with award-winning professionals across creative fields")
st.divider()

# 首次访问提示（新增）
if st.session_state.first_visit and not st.session_state.messages:
    with st.info("👋 Welcome! Select a role from the sidebar and start chatting with creative experts."):
        st.write("Example questions:")
        st.code("Film Director: How to shoot a emotional dialogue scene?")
        st.code("Sci-Fi Writer: What's a unique alien social structure?")
    st.session_state.first_visit = False  # 仅显示一次

# 核心聊天逻辑
if not st.session_state.api_key:
    st.warning("⚠️ Please enter your OpenAI API key in the sidebar to start chatting")
elif not st.session_state.selected_role:
    st.info("ℹ️ Select a creative expert from the sidebar to begin the conversation")
else:
    # 显示聊天历史（带角色头像）
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            # 助手消息带角色头像
            with st.chat_message(
                msg["role"],
                avatar=ROLES[st.session_state.selected_role]["avatar"]
            ):
                st.markdown(msg["content"])
        else:
            # 用户消息带默认头像
            with st.chat_message(msg["role"], avatar="👤"):
                st.markdown(msg["content"])
    
    # 用户输入框
    if prompt := st.chat_input(
        f"Ask {st.session_state.selected_role} a question...",
        key="chat_input"
    ):
        # 添加用户消息到历史
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # 生成角色回复（带加载动画）
        with st.chat_message(
            "assistant",
            avatar=ROLES[st.session_state.selected_role]["avatar"]
        ):
            # 显示加载状态
            with st.spinner(f"{st.session_state.selected_role} is thinking..."):
                # 构建对话上下文
                full_messages = [
                    {"role": "system", "content": ROLES[st.session_state.selected_role]["prompt"]}
                ] + st.session_state.messages
                
                try:
                    # 初始化OpenAI客户端（最新版本语法）
                    client = OpenAI(api_key=st.session_state.api_key)
                    
                    # 流式获取回复
                    stream = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=full_messages,
                        stream=True,
                        temperature=0.8  # 更高的随机性，增强创造性
                    )
                    
                    # 流式输出（带动态效果）
                    response = ""
                    response_placeholder = st.empty()
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            response += chunk.choices[0].delta.content
                            response_placeholder.markdown(response + "▌")  # 光标动画
                            time.sleep(0.02)  # 控制输出速度
                    response_placeholder.markdown(response)  # 最终显示
                    
                    # 保存回复到历史
                    st.session_state.messages.append({"role": "assistant", "content": response})
                
                except Exception as e:
                    # 详细错误提示（比参考链接更友好）
                    error_msg = str(e)
                    if "insufficient_quota" in error_msg:
                        st.error("💸 Quota Exceeded: Please check your OpenAI billing settings to add a payment method.")
                    elif "invalid_api_key" in error_msg:
                        st.error("🔑 Invalid API Key: Please check your key and try again.")
                    else:
                        st.error(f"❌ Error: {error_msg}")

# 页脚（新增）
st.markdown("""
<div style="margin-top: 2rem; text-align: center; color: #94a3b8; font-size: 0.9rem;">
    RoleCraft © 2023 | Chat with creative experts powered by OpenAI
</div>
""", unsafe_allow_html=True)
