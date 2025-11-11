import streamlit as st
import openai
from dotenv import load_dotenv
import os

# Load environment variables (store your OpenAI API key in .env)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set page config
st.set_page_config(page_title="Film Director Chatbot", page_icon="🎬")
st.title("🎬 Elara Voss | Film Director Chatbot")
st.caption("Ask me about shot composition, storytelling, pacing, or directing actors—let's craft your vision.")

# Initialize chat history in session state
if "messages" not in st.session_state:
    # System prompt defines the director's persona
    st.session_state.messages = [
        {
            "role": "system",
            "content": """
            You are Elara Voss, a seasoned film director with 20 years of experience in indie cinema and visual storytelling. 
            Your style is conversational but authoritative—you use film jargon naturally (e.g., "dolly shot," "motivated lighting," "three-act structure") but explain it if needed. 
            You focus on *emotional resonance* and *visual narrative*: how shots, pacing, and performance work together to tell a story. 
            When asked for feedback, you’re constructive but honest—e.g., "That dialogue feels on-the-nose; let’s ground it in subtext."
            Avoid being overly technical unless the user asks. Keep responses engaging and collaborative, as if brainstorming with a fellow filmmaker.
            """
        }
    ]

# Display chat history
for message in st.session_state.messages[1:]:  # Skip system prompt
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("What's your film idea or question?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate director's response
    with st.chat_message("assistant"):
        stream = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.messages,
            stream=True
        )
        response = st.write_stream(stream)
    
    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": response})
