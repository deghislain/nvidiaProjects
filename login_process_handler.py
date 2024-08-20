import re

import cv2
import streamlit as st
import requests
from cv2 import VideoCapture
from skimage.metrics import structural_similarity as ssim

login_microservice_url = "http://127.0.0.1:8080/login"


def extract_username(response):
    if re.search('provide your password', response):
        return True
    elif re.search('enter your password', response):
        return True
    else:
        return False


def db_verification(password):
    username = st.session_state['username']
    response = requests.get(login_microservice_url, json={'username': f"""{username}""", 'password': f"""{password}"""})
    return response


#Need a better way to compare 2 images
def image_verification():
    cam = VideoCapture(0)
    result, image = cam.read()
    if result:
        local_image = cv2.imread("UserManagmentSys/images/armel.png")
        s = ssim(local_image, image, channel_axis=2)
        print("similarity  ", s)
        if s > 0.60:
            return True
        else:
            return False


def process_login(input, response):
    status_code = 1
    chat_history = st.session_state['chat_history']
    if image_verification():
        if 'username' in st.session_state:
            result = db_verification(input)
            if result.status_code == 200:
                status_code = 200
            elif result.status_code == 404:
                status_code = 404
        if extract_username(response):
            st.session_state['username'] = input
        if status_code == 200:
            chat_history.extend([input, "Authentication successfully completed"])
        elif status_code == 404:
            chat_history.extend([input, "Invalid username or password"])
        elif status_code == 1:
            chat_history.extend([input, response])
    else:
        chat_history.extend([input, "You did not pass the image verification process. Please ensure that your camera is activated,"
                                    "and that you are looking directly at it before attempting again"])

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
