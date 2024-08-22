import streamlit as st
from langchain_core.prompts import PromptTemplate


def get_the_welcome_prompt(human_input):
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    chat_history = st.session_state['chat_history']
    template = f"""
               You are chatbot responsible for managing the user authentication process.
               You start welcoming the user then you ask what you can do for him. 
               Ensure a smooth user experience by providing clear instructions and feedback throughout the process.
               Be concise.

           {chat_history}
           Human: {human_input}
           Chatbot:"""

    return PromptTemplate(input_variables=["chat_history", "human_input"], template=template)


def get_the_login_prompt(human_input):
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    chat_history = st.session_state['chat_history']
    template = f"""
               You are chatbot responsible for managing the authentication process. Please follow these steps 
               to authenticate the user:
               Request Username: Start by asking the user to provide their username.
               Request Password: Once the username is provided, ask the user to enter their password.
               Ensure a smooth user experience by providing clear instructions and feedback throughout the process.
               Be concise.

           {chat_history}
           Human: {human_input}
           Chatbot:"""

    return PromptTemplate(input_variables=["chat_history", "human_input"], template=template)
