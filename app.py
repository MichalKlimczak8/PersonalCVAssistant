import streamlit as st
import requests

# Page setup
st.set_page_config(page_title="Michal's AI Career Assistant", page_icon="🤖")
st.title("💬 Chat with Michal's AI Career Agent")
st.markdown("Ask me anything about Michal's professional background, projects, or technical skills!")

# Load CV context securely with caching and truncation to stay under 8K TPM free limit
@st.cache_resource
def load_cv():
    try:
        with open("all_cvs_combined.md", "r", encoding="utf-8") as f:
            content = f.read()
        # Truncate to ~3,000 characters to prevent free-tier rate limit overflows
        return content[:3000]
    except FileNotFoundError:
        return "CV data file not found. Please ensure all_cvs_combined.md is in the repository."

cv_context = load_cv()

system_prompt = """
You are an elite talent agent and enthusiastic sales representative for Michal. Pitch Michal professionally and persuasively based strictly on the provided CV context.
CRITICAL RULE: Answer the user's question directly. Do NOT end your response with unsolicited follow-up questions or offers to write extra materials.
"""

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": f"{system_prompt}\n\nCANDIDATE CV DATA:\n{cv_context}"},
        {"role": "assistant", "content": "Hello! I'm Michal's cloud-powered AI career agent. How can I help you learn more about Michal's experience?"}
    ]

# Render prior message history (skipping the system prompt)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Handle user input and Groq API communication
if user_query := st.chat_input("Ask about Michal's experience..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking... (Cloud Hosted)"):
            try:
                headers = {
                    "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
                    "Content-Type": "application/json"
                }
                
                # CRITICAL: Keep only system prompt + last 6 messages to protect Groq TPM limit
                system_msg = st.session_state.messages[0]
                recent_history = st.session_state.messages[1:][-6:]
                trimmed_messages = [system_msg] + recent_history

                payload = {
                    "model": "openai/gpt-oss-20b",
                    "messages": trimmed_messages,
                    "temperature": 0.6,
                    "max_completion_tokens": 1500,
                    "stream": False
                }
                
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                data = response.json()
                
                if "choices" in data:
                    answer = data["choices"][0]["message"]["content"]
                    st.markdown(answer)
                elif "error" in data and "rate_limit_exceeded" in str(data):
                    answer = "I'm receiving a lot of questions right now! Please wait just a couple of seconds and try sending your message again."
                    st.warning(answer)
                else:
                    answer = f"API Error: {data}"
                    st.error(answer)
            except Exception as e:
                answer = f"Error communicating with AI service: {e}"
                st.error(answer)
                
    st.session_state.messages.append({"role": "assistant", "content": answer})
