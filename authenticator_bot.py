from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import login_process_handler as lpl
import streamlit as st
import user_prompts as up
import re
import registration_process_handler as rph

login_microservice_url = "http://127.0.0.1:8080/login"


def display_chat_history():
    chat_history = st.session_state['chat_history']
    count = 0
    for m in chat_history:
        if count % 2 == 0:
            output = st.chat_message("user")
            output.write(m)
        else:
            output = st.chat_message("assistant")
            output.write(m)
        count += 1


def select_process(input):
    if re.search('login', input):
        return "login"
    elif re.search('new account', input):
        return "registration"


def get_the_model(prompt):
    memory = ConversationBufferMemory(memory_key="chat_history")

    llm = ChatNVIDIA(model="meta/llama3-8b-instruct", temperature=0)
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=memory,
    )
    return llm_chain


input = st.chat_input("Say hi to start a new conversation")
if 'process_status' not in st.session_state:
    st.session_state['process_status'] = 0
if input:
    if select_process(input) == "login" or st.session_state['process_status'] == 2:
        login_prompt = up.get_the_login_prompt(input)
        llm_chain = get_the_model(login_prompt)
        response = llm_chain.predict(human_input=input)
        try:
            lpl.process_login(input, response)
        except Exception as ex:
            chat_history = st.session_state['chat_history']
            chat_history.extend([input, "Error during the authentication process. Please, try again later"])
            print("An error occurred during your login", ex)
        st.session_state['process_status'] = 2
    elif select_process(input) == "registration" or st.session_state['process_status'] == 3:
        reg_prompt = up.get_the_registration_prompt(input)
        llm_chain = get_the_model(reg_prompt)
        response = llm_chain.predict(human_input=input)
        try:
            result = rph.create_new_account(input, response)
            if result:
                chat_history = st.session_state['chat_history']
                chat_history.extend([input, "Congratulation for the creation of your new account"])
            st.session_state['process_status'] = 3
        except Exception as ex:
            chat_history = st.session_state['chat_history']
            chat_history.extend([input, "Error during the creation of your new account. Please, try again later"])
            print("An error occurred during your new account creation", ex)

    else:
        welcome_prompt = up.get_the_welcome_prompt(input)
        llm_chain = get_the_model(welcome_prompt)
        response = llm_chain.predict(human_input=input)
        chat_history = st.session_state['chat_history']
        chat_history.extend([input, response])

    display_chat_history()
