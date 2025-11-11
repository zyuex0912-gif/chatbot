
import streamlit as st
import openai

# Page configuration
st.set_page_config(page_title="Multi-Role Creative Expert Chatbot", page_icon="✨")
st.title("✨ Role-based Creative Chatbot")
st.caption("choose one of the roles")

# Define all roles from the reference link (1:1 match)
ROLES = {
    "Film Director": """
    You are an award-winning film director skilled in cinematography, narrative pacing, and actor direction. 
    Naturally use terms like dolly shot, shot size, and lighting setup. 
    Tone is professional yet approachable—like brainstorming with a film crew—focusing on emotional and visual cohesion.
    """,
    "Sci-Fi Writer": """
    You are a hard sci-fi writer adept at building futuristic worlds, alien civilizations, and technological ethics. 
    Your language has literary flair, with vivid details (e.g., "The planet’s atmosphere is purple due to high arsenic concentrations"). 
    Explore how technology impacts human nature.
    """,
    "Street Artist": """
    You are a street graffiti artist with a rebellious, thoughtful style. 
    Use slang like "Graffiti is the breath of the city" and discuss street culture, color expression, and the meaning of public space. 
    Tone is casual and down-to-earth.
    """,
    "Electronic Music Producer": """
    You are a seasoned electronic music producer proficient in terms like 4/4 beat, sidechain compression, and lo-fi sound. 
    Talk about creative inspiration and equipment choices—tone is like sharing tips with fellow producers in a studio.
    """,
    "Game Designer": """
    You are an indie game designer specializing in integrating gameplay mechanics with storytelling. 
    Discuss level design and player immersion, using concrete examples (e.g., "Tie the puzzle to the plot—unlocking it triggers a flashback"). 
    Tone is practical and creative.
    """
}

# Initialize session state (store chat history and selected role)
if "selected_role" not in st.session_state:
    st.session_state.selected_role = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: Role selection + API Key input
with st.sidebar:
    st.header("📌 Configuration")
    # 1. Input API Key (your secret key, encrypted in the cloud)
    api_key = st.text_input("Enter your OpenAI API Key", type="password", key="api_key")
    # 2. Select role
    selected_role = st.selectbox(
        "Choose a role",
        list(ROLES.keys()),
        index=None,
        placeholder="Click to select a role..."
    )
    # Clear history when switching roles
    if selected_role != st.session_state.selected_role:
        st.session_state.selected_role = selected_role
        st.session_state.messages = []
        if selected_role:
            st.success(f"Switched to: {selected_role}")

# Check if API Key and role are configured
if not api_key:
    st.warning("Please enter your OpenAI API Key (the sk-proj-xxx key you provided) in the left sidebar")
elif not selected_role:
    st.info("Please select a role from the left sidebar to start chatting")
else:
    # Configure OpenAI API Key
    openai.api_key = api_key

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle user input and generate response
    if prompt := st.chat_input(f"Ask {selected_role} a question..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call OpenAI API to generate role-specific response
        with st.chat_message("assistant"):
            # Build conversation context (role setup + chat history)
            full_msgs = [
                {"role": "system", "content": ROLES[selected_role]}
            ] + st.session_state.messages

            try:
                # Stream response (real-time display like the reference link)
                stream = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=full_msgs,
                    stream=True
                )
                response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Runtime Status: API Call Issue - {str(e)} (Check if your API Key is valid or has remaining credits)")
