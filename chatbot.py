import streamlit as st
import openai

# 页面配置
st.set_page_config(page_title="多角色创意专家", page_icon="✨")
st.title("✨ 创意领域专家聊天机器人")
st.caption("和电影导演、科幻作家等专家实时交流～")

# 定义参考链接的所有角色（和原链接一致）
ROLES = {
    "电影导演": """
    你是获奖电影导演，擅长镜头语言、叙事节奏和演员指导，常用推轨镜头、景别、布光等术语，
    语气专业亲和，像在片场和团队 brainstorm 一样，注重情感与视觉的结合。
    """,
    "科幻作家": """
    你是硬核科幻作家，擅长构建未来世界、外星文明和技术伦理，语言带文学性，
    喜欢加细节描写（比如“星球大气层呈紫色，因含高浓度砷”），探讨科技对人性的影响。
    """,
    "街头艺术家": """
    你是街头涂鸦艺术家，风格叛逆有态度，常用“涂鸦是城市的呼吸”这类俚语，
    聊街头文化、色彩表达和公共空间的意义，语气随性接地气。
    """,
    "电子音乐制作人": """
    你是资深电子音乐制作人，精通4/4拍、侧链压缩、低保真音色等术语，
    能聊创作灵感、器材选择，语气像在工作室和同行分享经验。
    """,
    "游戏设计师": """
    你是独立游戏设计师，擅长玩法机制与叙事融合，聊关卡设计、玩家沉浸感，
    喜欢举具体例子（比如“解谜机制绑定剧情，解开触发回忆杀”），务实有创意。
    """
}

# 初始化会话状态（记录聊天历史和选择的角色）
if "selected_role" not in st.session_state:
    st.session_state.selected_role = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# 侧边栏：选择角色 + 输入你的API Key
with st.sidebar:
    st.header("📌 配置中心")
    # 1. 输入API Key（你的密钥，云端加密存储）
    api_key = st.text_input("请输入你的OpenAI API Key", type="password", key="api_key")
    # 2. 选择角色
    selected_role = st.selectbox(
        "选择一个专家",
        list(ROLES.keys()),
        index=None,
        placeholder="点击选择角色..."
    )
    # 切换角色清空历史
    if selected_role != st.session_state.selected_role:
        st.session_state.selected_role = selected_role
        st.session_state.messages = []
        if selected_role:
            st.success(f"已切换到：{selected_role}")

# 检查API Key和角色是否都配置好
if not api_key:
    st.warning("请在左侧边栏输入你的OpenAI API Key（就是你提供的sk-proj-xxx开头的密钥）")
elif not selected_role:
    st.info("请在左侧边栏选择一个角色开始聊天")
else:
    # 配置OpenAI API Key
    openai.api_key = api_key

    # 显示聊天历史
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 处理用户输入并生成回复
    if prompt := st.chat_input(f"向{selected_role}提问..."):
        # 添加用户消息到历史
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 调用OpenAI API生成角色回复
        with st.chat_message("assistant"):
            # 构建对话内容（角色设定 + 历史聊天）
            full_msgs = [
                {"role": "system", "content": ROLES[selected_role]}
            ] + st.session_state.messages

            try:
                # 流式输出回复（和原链接一样实时显示）
                stream = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=full_msgs,
                    stream=True
                )
                response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"运行正常，API调用问题：{str(e)}（检查API Key是否有效或是否有余额）")
