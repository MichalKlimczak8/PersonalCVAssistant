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
                
                # Using the exact model ID from your Groq dashboard
                payload = {
                    "model": "openai/gpt-oss-20b",
                    "messages": st.session_state.messages,
                    "temperature": 0.6,
                    "max_completion_tokens": 2048,
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
                else:
                    answer = f"API Error: {data}"
                    st.error(answer)
            except Exception as e:
                answer = f"Error communicating with AI service: {e}"
                st.error(answer)
                
    st.session_state.messages.append({"role": "assistant", "content": answer})
