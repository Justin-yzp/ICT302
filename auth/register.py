import streamlit as st
from db.db_handler import add_user


def register():
    st.title("Register")

    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if password == confirm_password:
            try:
                add_user(username, password)
                st.success("User registered successfully")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.error("Passwords do not match")
