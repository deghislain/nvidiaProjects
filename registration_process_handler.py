import streamlit as st
from cv2 import VideoCapture, imwrite
import re
from UserManagmentSys.User import User
import uuid
import utilities as util
import requests
import json

create_microservice_url = "http://127.0.0.1:8080/create"
username_microservice_url = "http://127.0.0.1:8080/username"


def capture_user_picture():
    if st.session_state['process_status'] >= 6:
        return True

    try:
        cam = VideoCapture(0)
        result, image = cam.read()
        if result:
            if 'username' in st.session_state:
                username = st.session_state['username']
                imwrite(f"UserManagmentSys/images/{username}.png", image)
                st.session_state['process_status'] = 6
            return True
        else:
            return False
    except Exception as ex:
        chat_history = st.session_state['chat_history']
        chat_history.extend([input, "Error while capturing your image. Please ensure that your camera is activated,"
                                    "and that you are looking directly at it before attempting again"])
        print("Error while capturing your image", ex)


def store_user(input):
    user_id = uuid.uuid4()
    hash_password = util.hash_password(input)
    user = User(str(user_id), st.session_state['username'], hash_password, st.session_state['firstname'],
                st.session_state['lastname'], st.session_state['email'], st.session_state['phone_number'],
                st.session_state['address'])
    json_user = json.dumps(user.__dict__)
    newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    result = requests.post(create_microservice_url, json_user, headers=newHeaders)
    return result


def create_new_account(input, response):
    previous_response = ""
    if 'previous_response' not in st.session_state:
        st.session_state['previous_response'] = response
    else:
        previous_response = st.session_state['previous_response']
        st.session_state['previous_response'] = response
    chat_history = st.session_state['chat_history']
    if (re.search('[Pp]lease choose a unique (username|name)', previous_response)
            or re.search('This username is already in use', previous_response)):
        if check_username_availability(input):
            if 'username' not in st.session_state:
                st.session_state['username'] = input
        else:
            chat_history.extend([input, "This username is already in use, try a different one please."])
            st.session_state['previous_response'] = "This username is already in use, try a different one please."
            return False
    elif re.search('^Thank.*please.*first name.$', previous_response):
        if 'firstname' not in st.session_state:
            st.session_state['firstname'] = input
    elif re.search('^Thank.*please.*last name.$', previous_response):
        if 'lastname' not in st.session_state:
            st.session_state['lastname'] = input
    elif re.search('^Thank.*please.*email address.$', previous_response):
        if 'email' not in st.session_state:
            st.session_state['email'] = input
    elif re.search('^Thank.*please.*phone number.*', previous_response):
        if 'phone_number' not in st.session_state:
            st.session_state['phone_number'] = input
    elif re.search('^Thank.*please.*address.$', previous_response):
        if 'address' not in st.session_state:
            st.session_state['address'] = input
    elif re.search('please create a secure password', previous_response):
        if capture_user_picture() and store_user(input).status_code == 200:
            # removing username from session so that we can login with the new useFrname
            del st.session_state['username']
            return True

    chat_history.extend([input, response])
    return False


def check_username_availability(username):
    response = requests.get(username_microservice_url, json={'username': f"""{username}"""})
    if response and response.text == "Username available":
        return True
    else:
        return False


