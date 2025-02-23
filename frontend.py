import streamlit as st
import requests
import plotly.graph_objects as go
import json

st.set_page_config(
    page_title="Titanic Dataset Analysis Chatbot",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .stApp { max-width: 1200px; margin: 0 auto; }
    .chat-message { padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; max-width: 80%; }
    .user-message { background-color: #4f46e5; color: white; margin-left: auto; }
    .bot-message { background-color: #f3f4f6; color: #1f2937; }
    .stButton button { background-color: #4f46e5; color: white; border-radius: 0.5rem; padding: 0.5rem 1rem; border: none; }
    .stButton button:hover { background-color: #4338ca; }
    </style>
    """, unsafe_allow_html=True)

if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        'type': 'bot',
        'content': """Hello! I'm your Titanic dataset analysis assistant. 
        You can ask questions like:  
        - "What was the overall survival rate?"  
        - "What percentage of passengers were male?"  
        - "Show me a histogram of passenger ages"  
        - "How many passengers embarked from each port?"  
        """
    })

API_URL = "http://localhost:8000/analyze"

st.title("🚢 Titanic Dataset Analysis Chatbot")

for message in st.session_state.messages:
    with st.container():
        if message['type'] == 'user':
            st.markdown(f"""
                <div class="chat-message user-message">
                    {message['content']}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="chat-message bot-message">
                    {message['content']}
                </div>
            """, unsafe_allow_html=True)
            if 'plot' in message and message['plot']:
                fig = go.Figure(message['plot'])
                st.plotly_chart(fig, use_container_width=True)

with st.container():
    with st.form(key='chat_form'):
        user_input = st.text_input("Ask a question about the Titanic dataset...")
        submit_button = st.form_submit_button("Send")

        if submit_button and user_input:
            st.session_state.messages.append({'type': 'user', 'content': user_input})
            
            try:
                response = requests.post(API_URL, json={'text': user_input})
                result = response.json()
                
                bot_message = {'type': 'bot', 'content': result['text']}
                if result.get('plot'):
                    bot_message['plot'] = result['plot']
                
                st.session_state.messages.append(bot_message)
                st.rerun()
            except Exception as e:
                st.error(f"Error communicating with the API: {str(e)}")
