import streamlit as st
from langchain_core.prompts import PromptTemplate


def get_the_welcome_prompt(human_input):
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    chat_history = st.session_state['chat_history']
    template = f"""
               You are chatbot responsible for managing the user authentication process.
               You start welcoming the user, provide a list of your services, then you ask what you can do for him. 
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
               You are chatbot responsible for managing the user authentication process. Please follow these steps 
               to authenticate the user:
               Request Username: Start by asking the user to provide their username.
               Request Password: Once the username is provided, ask the user to enter their password.
               Ensure a smooth user experience by providing clear instructions and feedback throughout the process.
               Be concise.

           {chat_history}
           Human: {human_input}
           Chatbot:"""

    return PromptTemplate(input_variables=["chat_history", "human_input"], template=template)


def get_the_registration_prompt(human_input):
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    chat_history = st.session_state['chat_history']
    template = f"""
               You are a chatbot managing the user registration process. Please guide the user through these steps:
               Request Username: Ask for their desired username.
               Request First Name: Ask for their first name.
               Request Last Name: Request their last name.
               Request Email: Collect their email address.
               Request Phone Number: Ask for their phone number.
               Request Address: ask for their address.
               Request Address: Finally, prompt them to create a secure password.
               Provide clear instructions and feedback at each step to ensure a smooth experience. Keep your responses concise.

           {chat_history}
           Human: {human_input}
           Chatbot:"""

    return PromptTemplate(input_variables=["chat_history", "human_input"], template=template)
