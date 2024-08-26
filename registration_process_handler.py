import streamlit as st
from cv2 import VideoCapture, imwrite
import re
from UserManagmentSys.User import User
import uuid
import utilities as util
import requests
import json

login_microservice_url = "http://127.0.0.1:8080/create"


def capture_user_picture():
    if st.session_state['process_status'] >= 4:
        return True

    cam = VideoCapture(0)
    result, image = cam.read()
    if result:
        if 'username' in st.session_state:
            username = st.session_state['username']
            imwrite(f"UserManagmentSys/images/{username}.png", image)
            st.session_state['process_status'] = 4


def store_user(input):
    user_id = uuid.uuid4()
    hash_password = util.hash_password(input)
    user = User(str(user_id), st.session_state['username'], hash_password, st.session_state['firstname'],
                st.session_state['lastname'], st.session_state['email'], st.session_state['phone_number'],
                st.session_state['address'])
    json_user = json.dumps(user.__dict__)
    newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    result = requests.post(login_microservice_url, json_user, headers=newHeaders)
    return result


def create_new_account(input, response):
    previous_response = ""
    if 'previous_response' not in st.session_state:
        st.session_state['previous_response'] = response
    else:
        previous_response = st.session_state['previous_response']
        st.session_state['previous_response'] = response
    chat_history = st.session_state['chat_history']

    if re.search('please choose a unique username', previous_response):
        if 'username' not in st.session_state:
            st.session_state['username'] = input
    elif (re.search('please provide your first name', previous_response)
          or re.search('please enter your first name', previous_response)):
        if 'firstname' not in st.session_state:
            st.session_state['firstname'] = input
    elif (re.search('please provide your last name', previous_response)
          or re.search('please enter your last name', previous_response)):
        if 'lastname' not in st.session_state:
            st.session_state['lastname'] = input
    elif (re.search('please provide your email address', previous_response)
          or re.search('please enter your email address', previous_response)):
        if 'email' not in st.session_state:
            st.session_state['email'] = input
    elif (re.search('please provide your phone number', previous_response)
          or re.search('please enter your phone number', previous_response)):
        if 'phone_number' not in st.session_state:
            st.session_state['phone_number'] = input
    elif (re.search('please provide your address', previous_response)
          or re.search('please enter your address', previous_response)):
        if 'address' not in st.session_state:
            st.session_state['address'] = input
    elif re.search('please create a secure password', previous_response):
        if store_user(input).status_code == 200:
            return True

    chat_history.extend([input, response])
    return False

