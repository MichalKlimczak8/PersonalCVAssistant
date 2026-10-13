with st.chat_message("assistant"):
            with st.spinner("Thinking... (Cloud Hosted)"):
                try:
                    headers = {
                        "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
                        "Content-Type": "application/json"
                    }
                    
                    # 1. Dynamically fetch available models from Groq to prevent 404s
                    models_resp = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
                    available_models = [m["id"] for m in models_resp.json().get("data", [])]
                    
                    # Pick the best available model or default to the first one found
                    chosen_model = "llama-3.1-8b-instant"
                    if available_models:
                        # Prefer 8b-instant or 70b-versatile if present
                        preferred = [m for m in available_models if "8b-instant" in m or "70b" in m]
                        chosen_model = preferred[0] if preferred else available_models[0]

                    payload = {
                    "model": "qwen/qwen3.8-27b",
                    "messages": st.session_state.messages,
                    "temperature": 0.6,
                    "max_tokens": 2048
                    }
                    
                    response = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    data = response.json()
                    
                    if "choices" in data:
                        answer = data["choices"][0]["message"]["content"]
                        st.markdown(answer)
                    else:
                        answer = f"API Error: {data}"
                        st.error(answer)
                except Exception as e:
                    answer = f"Error communicating with AI service: {e}"
                    st.error(answer)
                
        st.session_state.messages.append({"role": "assistant", "content": answer})
