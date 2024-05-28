import streamlit as st
from db.db_handler import validate_user

def login():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if validate_user(username, password):
            st.success("Login successful")
            st.session_state['logged_in'] = True
            st.session_state['username'] = username

            # Redirect to the register page if the user is an admin
            if username == 'admin':  # Replace with actual admin username check
                st.session_state['page'] = 'register'
            else:
                st.session_state['page'] = 'dashboard'
        else:
            st.error("Invalid username or password")
