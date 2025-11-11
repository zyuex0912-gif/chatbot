import streamlit as st
from openai import OpenAI

# 页面基础配置（和参考链接风格一致）
st.set_page_config(
    page_title="多角色创意专家聊天",
    page_icon="🎭",
    layout="wide"
)

# 自定义页面样式（贴近参考链接视觉）
st.markdown("""
    <style>
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #2d3748;
    }
    .role-select {
        margin-bottom: 1.5rem;
    }
    .chat-input {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# 定义参考链接同款角色（5个核心创意领域专家）
ROLES = {
    "电影导演": """
    你是获奖电影导演，拥有15年独立电影与商业片拍摄经验，擅长镜头语言设计、叙事节奏把控和演员指导。
    交流时自然使用推轨镜头、景别切换、布光技巧等专业术语，语气亲和且有决策力，像在片场和团队头脑风暴，
    注重情感表达与视觉呈现的融合，能快速给出具体可落地的拍摄建议。
    """,
    "科幻作家": """
    你是硬核科幻作家，曾出版多部雨果奖提名作品，擅长构建逻辑自洽的未来世界、外星文明和技术伦理体系。
    语言带文学性，喜欢加入细节描写（如“星球大气层呈深紫色，因高浓度甲烷与氩气混合”），
    探讨科技对人性、社会结构的深层影响，回复兼具想象力与科学性。
    """,
    "街头艺术家": """
    你是国际知名街头涂鸦艺术家，作品遍布全球12个城市，风格叛逆且充满社会思考。
    常用“涂鸦不是破坏，是城市无声的呐喊”这类表达，聊街头文化、色彩心理学、公共空间的艺术价值，
    语气随性接地气，带点街头文化的率真，能给出具体的创作主题和表现手法建议。
    """,
    "电子音乐制作人": """
    你是资深电子音乐制作人，擅长House、Techno、Lo-Fi等多种风格，拥有自己的独立工作室。
    精通4/4拍节奏设计、侧链压缩、低保真音色调制等专业术语，聊创作灵感、器材选择、混音技巧时，
    语气像在工作室和同行分享经验，通俗易懂且干货满满，能针对需求给出具体的制作思路。
    """,
    "游戏设计师": """
    你是独立游戏设计师，曾主导开发多款Steam畅销独立游戏，擅长玩法机制与叙事剧情的深度融合。
    交流时聚焦关卡设计、玩家沉浸感、交互逻辑，喜欢举具体例子（如“解谜机制绑定主角回忆，解开后解锁关键剧情”），
    语气务实有创意，能快速拆解需求并转化为可落地的游戏设计方案。
    """
}

# 初始化会话状态（记录聊天历史、选中角色、API Key）
if "selected_role" not in st.session_state:
    st.session_state.selected_role = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# 侧边栏配置（和参考链接布局一致）
with st.sidebar:
    st.markdown('<div class="sidebar-header">🎭 角色与配置</div>', unsafe_allow_html=True)
    
    # API Key 输入（密码类型，保护隐私）
    api_key = st.text_input(
        "请输入 OpenAI API Key",
        type="password",
        key="api_key_input",
        placeholder="sk-proj-xxx 开头的密钥",
        value=st.session_state.api_key
    )
    st.session_state.api_key = api_key  # 保存输入的密钥
    
    st.divider()
    
    # 角色选择下拉框
    st.markdown('<div class="role-select">选择聊天角色</div>', unsafe_allow_html=True)
    selected_role = st.selectbox(
        "点击选择专家",
        options=list(ROLES.keys()),
        index=None,
        placeholder="请选择一个角色...",
        key="role_select"
    )
    
    # 切换角色时清空聊天历史
    if selected_role != st.session_state.selected_role:
        st.session_state.selected_role = selected_role
        st.session_state.messages = []
        if selected_role:
            st.success(f"已切换至：{selected_role}")

# 主页面标题与说明
st.title("🎭 多角色创意专家聊天机器人")
st.caption("和电影导演、科幻作家等领域专家实时交流，获取专业见解～")
st.divider()

# 核心逻辑：检查配置 + 显示聊天
if not st.session_state.api_key:
    st.warning("⚠️ 请在左侧边栏输入有效的 OpenAI API Key 以开始聊天")
elif not st.session_state.selected_role:
    st.info("ℹ️ 请在左侧边栏选择一个角色，即可开始对话")
else:
    # 显示历史聊天记录
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # 用户输入框
    if prompt := st.chat_input(f"向 {st.session_state.selected_role} 提问...", key="chat_input"):
        # 添加用户消息到历史
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 生成角色回复（流式输出，和参考链接一致）
        with st.chat_message("assistant"):
            # 构建对话上下文（角色设定 + 历史消息）
            full_messages = [
                {"role": "system", "content": ROLES[st.session_state.selected_role]}
            ] + st.session_state.messages
            
            try:
                # 初始化 OpenAI 客户端（使用用户输入的密钥）
                client = OpenAI(api_key=st.session_state.api_key)
                
                # 流式调用 API
                stream = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=full_messages,
                    stream=True,
                    temperature=0.7  # 保持回复的自然度
                )
                
                # 逐段显示回复
                response = ""
                response_placeholder = st.empty()
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        response += chunk.choices[0].delta.content
                        response_placeholder.markdown(response)
                
                # 保存回复到历史
                st.session_state.messages.append({"role": "assistant", "content": response})
            
            except Exception as e:
                # 错误处理（明确提示问题类型）
                error_msg = str(e)
                if "invalid_api_key" in error_msg.lower():
                    st.error("❌ API Key 无效，请检查密钥是否正确或重新生成")
                elif "insufficient_quota" in error_msg.lower():
                    st.error("❌ 配额不足，请检查 OpenAI 账户余额或支付方式")
                else:
                    st.error(f"❌ 调用失败：{error_msg}")

# 页脚说明
st.markdown("""
    <div style="margin-top: 2rem; text-align: center; color: #666; font-size: 0.9rem;">
        提示：确保 API Key 已绑定支付方式，且网络可正常访问 OpenAI 服务
    </div>
""", unsafe_allow_html=True)
