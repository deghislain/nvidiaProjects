from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import streamlit as st


def get_the_model(human_input):
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    chat_history = st.session_state['chat_history']

    template = f"""
            You are chatbot responsible for managing the authentication process. Please follow these steps 
            to authenticate the user:
            Request Username: Start by asking the user to provide their username.
            Request Password: Once the username is provided, ask the user to enter their password.
            Authenticate User: Use the provided username and password with the CustomLoginTool to authenticate the user.
            Be sure to handle each step in sequence and confirm the credentials are correctly processed by the CustomLoginTool.
            Ensure a smooth user experience by providing clear instructions and feedback throughout the process.

        {chat_history}
        Human: {human_input}
        Chatbot:"""

    print("***********", chat_history)
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
    llm_chain, chat_history = get_the_model(input)
    response = llm_chain.predict(human_input=input)
    chat_history.extend([input, response])
    st.session_state['chat_history'] = chat_history
    count = 0
    for m in chat_history:
        if count % 2 == 0:
            output = st.chat_message("user")
            output.write(m)
        else:
            output = st.chat_message("assistant")
            output.write(m)
        count += 1
    print(response)
