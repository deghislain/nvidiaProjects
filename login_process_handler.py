import re
import streamlit as st
import requests

login_microservice_url = "http://127.0.0.1:8080/login"


def extract_username(response):
    if re.search('provide your password', response):
        return True
    elif re.search('enter your password', response):
        return True
    else:
        return False


def authenticate_user(password):
    username = st.session_state['username']
    response = requests.get(login_microservice_url, json={'username': f"""{username}""", 'password': f"""{password}"""})
    return response


def process_login(input, response):
    status_code = 1
    if 'username' in st.session_state:
        result = authenticate_user(input)
        if result.status_code == 200:
            status_code = 200
        elif result.status_code == 404:
            status_code = 404
    chat_history = st.session_state['chat_history']
    if extract_username(response):
        st.session_state['username'] = input
    if status_code == 200:
        chat_history.extend([input, "Authentication successfully completed"])
    elif status_code == 404:
        chat_history.extend([input, "Invalid username or password"])
    elif status_code == 1:
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
