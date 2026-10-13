import streamlit as st
import requests

st.set_page_config(page_title="Michal's AI Career Assistant", page_icon="🤖")
st.title("💬 Chat with Michal's AI Career Agent")
st.markdown("Ask me anything about Michal's professional background, projects, or technical skills!")

@st.cache_resource
def load_cv():
    with open("all_cvs_combined.md", "r", encoding="utf-8") as f:
        return f.read()

cv_context = load_cv()
system_prompt = """
You are an elite talent agent and enthusiastic sales representative for Michal. Pitch Michal professionally and persuasively based strictly on the provided CV context.
CRITICAL RULE: Answer the user's question directly. Do NOT end your response with unsolicited follow-up questions or offers to write extra materials.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": f"{system_prompt}\n\nCANDIDATE CV DATA:\n{cv_context}"},
        {"role": "assistant", "content": "Hello! I'm Michal's cloud-powered AI career agent. How can I help you learn more about Michal's experience?"}
    ]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

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
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": st.session_state.messages
                }
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                data = response.json()
                answer = data["choices"][0]["message"]["content"]
                st.markdown(answer)
            except Exception as e:
                    # Print the exact error and the full API response for debugging
                    st.error(f"Error details: {e}")
                    if 'data' in locals():
                        st.write("Raw API Response from Groq:", data)
                    else:
                        st.write("Raw HTTP Response text:", response.text)
            
    st.session_state.messages.append({"role": "assistant", "content": answer})
