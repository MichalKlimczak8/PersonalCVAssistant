import streamlit as st
import requests
import re

# Page setup
st.set_page_config(page_title="Michal's AI Career Assistant", page_icon="🤖")
st.title("💬 Chat with Michal's AI Career Agent")
st.markdown("Ask me anything about Michal's professional background, projects, or technical skills!")

# Load the full CV file once and cache it
@st.cache_resource
def load_full_cv():
    try:
        with open("all_cvs_combined.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "CV data file not found."

full_cv_text = load_full_cv()

def get_relevant_context(query, cv_text, max_chars=3500):
    """
    Scans the full CV text, finds sections relevant to the user query,
    and returns a focused snippet under max_chars to protect rate limits.
    """
    # Split the CV text into logical sections or paragraphs
    sections = re.split(r'\n(?=#{1,3}\s+)', cv_text)
    
    # Extract keywords from the user query (ignoring common stop words)
    stop_words = {"the", "and", "a", "to", "in", "is", "it", "you", "that", "he", "was", "for", "on", "are", "with", "as", "I", "my", "me", "do", "how", "what"}
    query_words = {w.lower() for w in re.findall(r'\b\w+\b', query) if w.lower() not in stop_words}
    
    scored_sections = []
    for section in sections:
        section_lower = section.lower()
        # Count how many query keywords match this section
        score = sum(1 for word in query_words if word in section_lower)
        scored_sections.append((score, section))
        
    # Sort sections by relevance score (highest first)
    scored_sections.sort(key=lambda x: x[0], reverse=True)
    
    # Build context by appending top matching sections until we hit the character budget
    selected_context = ""
    for score, section in scored_sections:
        if len(selected_context) + len(section) < max_chars:
            selected_context += "\n\n" + section
        else:
            # If a section is too big, take a partial slice of it
            remaining = max_chars - len(selected_context)
            if remaining > 200:
                selected_context += "\n\n" + section[:remaining]
            break
            
    # Fallback: If no keywords matched, just provide the beginning of the file
    if not selected_context.strip():
        selected_context = cv_text[:max_chars]
        
    return selected_context.strip()

system_prompt = """
You are an elite talent agent and enthusiastic sales representative for Michal. Pitch Michal professionally and persuasively based strictly on the provided CV context snippet.
CRITICAL RULE: Answer the user's question directly. Do NOT end your response with unsolicited follow-up questions or offers to write extra materials.
"""

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm Michal's cloud-powered AI career agent. How can I help you learn more about Michal's experience?"}
    ]

# Render prior message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle user input
if user_query := st.chat_input("Ask about Michal's experience..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking... (Searching Profile)"):
            try:
                # Dynamically pull only the relevant parts of your 100k+ char CV for this specific question
                dynamic_cv_snippet = get_relevant_context(user_query, full_cv_text)
                
                # Construct messages dynamically: System prompt + relevant CV context + recent history
                system_message = {
                    "role": "system", 
                    "content": f"{system_prompt}\n\nRELEVANT CANDIDATE CV DATA:\n{dynamic_cv_snippet}"
                }
                
                # Keep only the last 6 messages of conversation history to protect TPM limits
                recent_history = [m for m in st.session_state.messages if m["role"] != "system"][-6:]
                trimmed_messages = [system_message] + recent_history

                headers = {
                    "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
                    "Content-Type": "application/json"
                }
                
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
