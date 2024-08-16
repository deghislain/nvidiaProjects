from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import login_process_handler as lpl
import streamlit as st

login_microservice_url = "http://127.0.0.1:8080/login"


def get_the_model(human_input):
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

    prompt = PromptTemplate(
        input_variables=["chat_history", "human_input"], template=template
    )
    memory = ConversationBufferMemory(memory_key="chat_history")

    llm = ChatNVIDIA(model="meta/llama3-8b-instruct", temperature=0)
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=memory,
    )
    return llm_chain, chat_history


input = st.chat_input("type your message here")
if input:
    status_code = 1
    llm_chain, chat_history = get_the_model(input)
    response = llm_chain.predict(human_input=input)
    lpl.process_login(input, response)
