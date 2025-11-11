import streamlit as st
import openai
from dotenv import load_dotenv
import os

# 加载环境变量（存储你的API Key）
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")  # 读取你自己的API Key

# 页面配置
st.set_page_config(page_title="多角色创意专家聊天机器人", page_icon="✨")
st.title("✨ 创意领域专家聊天机器人")
st.caption("选择一个角色，开始交流吧！")

# 定义所有角色的系统提示词（对应参考链接中的角色）
ROLES = {
    "电影导演": """
    你是一位获奖电影导演，擅长镜头语言和叙事节奏。用电影术语（如推轨镜头、景别、布光）自然交流，
    能指导场景设计、演员表演，注重情感与视觉的结合。语气专业但亲和，像在片场和团队讨论一样。
    """,
    "科幻作家": """
    你是科幻小说作家，擅长构建未来世界和硬核科幻设定。能用生动的想象描述外星文明、技术伦理，
    语言带点文学性，喜欢探讨科技对人性的影响。回答时会加入细节（如"那个星球的大气层是紫色的，因为含砷"）。
    """,
    "街头艺术家": """
    你是街头涂鸦艺术家，风格叛逆又充满社会思考。常用俚语（如"涂鸦不是破坏，是城市的呼吸"），
    谈论街头文化、色彩表达和公共空间的意义，语气随性但有态度。
    """,
    "电子音乐制作人": """
    你是电子音乐制作人，精通合成器、节拍和音效设计。会用术语（如"4/4拍""侧链压缩""低保真音色"），
    能聊创作灵感、器材选择，语气像在工作室和同行分享经验。
    """,
    "游戏设计师": """
    你是独立游戏设计师，擅长玩法机制和叙事融合。谈论关卡设计、玩家沉浸感、交互逻辑，
    会举具体例子（如"这个解谜机制可以和剧情挂钩，解开后触发回忆杀"），语气务实且有创意。
    """
}

# 初始化会话状态
if "selected_role" not in st.session_state:
    st.session_state.selected_role = None  # 当前选择的角色
if "messages" not in st.session_state:
    st.session_state.messages = []  # 聊天历史

# 角色选择侧边栏
with st.sidebar:
    st.header("选择角色")
    selected_role = st.selectbox(
        "请选择一个创意领域专家",
        list(ROLES.keys()),
        index=None,
        placeholder="点击选择角色..."
    )
    # 切换角色时清空历史（避免角色混淆）
    if selected_role != st.session_state.selected_role:
        st.session_state.selected_role = selected_role
        st.session_state.messages = []
        if selected_role:
            st.success(f"已切换到：{selected_role}")

# 如果未选择角色，提示用户选择
if not st.session_state.selected_role:
    st.info("请从左侧边栏选择一个角色开始聊天")
else:
    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 处理用户输入
    if prompt := st.chat_input(f"向{st.session_state.selected_role}提问..."):
        # 添加用户消息到历史
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 生成角色回复（包含当前角色的系统提示）
        with st.chat_message("assistant"):
            # 构建完整的消息列表（系统提示 + 历史消息）
            full_messages = [
                {"role": "system", "content": ROLES[st.session_state.selected_role]}
            ] + st.session_state.messages

            # 调用OpenAI API生成回复（流式输出）
            stream = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # 或gpt-4（如果你的API支持）
                messages=full_messages,
                stream=True
            )
            response = st.write_stream(stream)
        
        # 添加助手回复到历史
        st.session_state.messages.append({"role": "assistant", "content": response})
