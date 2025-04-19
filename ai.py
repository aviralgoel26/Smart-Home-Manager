import streamlit as st
import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Page Configuration
st.set_page_config(
    page_title="🏠 Smart Home Manager Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Apply Aesthetic CSS Styling

st.markdown(
    """
    <style>
        body {
            background-color: #87ceeb;
        }
        .stApp {
            background: rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 16px;
            padding: 2rem;
            font-family: 'Segoe UI', sans-serif;
            color: #003b4f;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
        }
        .stChatMessage {
            background: rgba(255, 255, 255, 0.8);
            padding: 1rem;
            border-radius: 1rem;
            margin-bottom: 1rem;
            color: #003b4f;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1);
            animation: fadeIn 0.3s ease-in-out;
        }
        .stChatInput > div {
            background-color: rgba(255,255,255,0.9);
            padding: 1rem;
            border-radius: 10px;
            color: #004d40;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        }
        .stSidebar {
            background-color: rgba(255,255,255,0.4);
            border-radius: 12px;
            padding: 1rem;
        }
        .stButton>button {
            background-color: #00acc1 !important;
            color: white !important;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #00838f !important;
        }
        .stTextInput>div>div>input {
            background-color: rgba(255,255,255,0.9);
            border-radius: 6px;
            padding: 0.6rem;
        }
        .stSelectbox>div>div>div>div {
            background-color: rgba(255,255,255,0.95);
            color: #004d40;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #004d40;
            text-shadow: 0 1px 1px rgba(255,255,255,0.5);
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
    """,unsafe_allow_html=True
)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hi there! 🤖 I’m your Smart Home Manager Chatbot. Ask me anything about smart home devices, automation, or energy-efficient tech!"
    }]

# Sidebar Settings
with st.sidebar:
    st.markdown("### 🔐 API Settings")
    api_key = st.text_input("OpenRouter API Key", type="password")
    st.markdown("[Get Free API Key](https://openrouter.ai/keys)")

    st.markdown("---")
    st.markdown("### ⚙️ Model Settings")
    model_name = st.selectbox(
        "Choose AI Model",
        ("deepseek/deepseek-r1-zero:free", "google/palm-2-chat-bison"),
        index=0
    )

    with st.expander("🔧 Advanced Settings"):
        temperature = st.slider("Creativity", 0.0, 1.0, 0.7)
        max_retries = st.number_input("Retry Attempts", 1, 5, 2)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hi again! 🤖 Ready to manage your smart home. Ask away!"
        }]

# Title and Description
st.title("🏠 Smart Home Manager Chatbot")
st.caption("Your personal assistant for smart home tech, automation & energy efficiency")

# Show Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(f"<div class='stChatMessage'>{msg['content']}</div>", unsafe_allow_html=True)

# Input Handling
if prompt := st.chat_input("Ask me about smart lights, thermostats, security..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(f"<div class='stChatMessage'>{prompt}</div>", unsafe_allow_html=True)

    if not api_key:
        with st.chat_message("assistant"):
            st.error("🔑 Please provide an API key in the sidebar to proceed.")
        st.stop()

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        attempts = 0

        while attempts < max_retries:
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://smart-home-chatbot.streamlit.app",
                        "X-Title": "Smart Home Manager"
                    },
                    json={
                        "model": model_name,
                        "messages": [
                            {
                                "role": "system",
                                "content": f"""You are a Smart Home Assistant expert.
Only respond to queries about smart home technology, devices, automation, IoT, energy-saving systems, and related technologies.

RULES:
1. RESPOND ONLY IN PLAIN TEXT
2. NEVER USE MARKDOWN, JSON, OR CODE BLOCKS
3. Format bullet points with hyphens (-)
4. Stay friendly, practical, and helpful
5. Say "I need to verify that" if you're unsure
6. DO NOT answer anything unrelated to smart homes
7. Current date: {time.strftime("%B %d, %Y")}
"""
                            },
                            *st.session_state.messages
                        ],
                        "temperature": temperature
                    },
                    timeout=15
                )

                response.raise_for_status()
                raw_response = response.json()['choices'][0]['message']['content']

                # Animate Response
                for chunk in raw_response.split():
                    full_response += chunk + " "
                    response_placeholder.markdown(f"<div class='stChatMessage'>{full_response}▌</div>", unsafe_allow_html=True)
                    time.sleep(0.03)

                response_placeholder.markdown(f"<div class='stChatMessage'>{full_response}</div>", unsafe_allow_html=True)
                break

            except requests.exceptions.RequestException as e:
                logging.error(f"Request Error: {str(e)}")
                response_placeholder.error(f"🌐 Network issue: {str(e)}")
                break

            except Exception as e:
                logging.error(f"Unexpected Error: {str(e)}")
                response_placeholder.error(f"❌ Unexpected issue: {str(e)}")
                break

    st.session_state.messages.append({"role": "assistant", "content": full_response})
