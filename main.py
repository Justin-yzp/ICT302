import streamlit as st
from auth.login import login
from pages.dashboard import dashboard
from pages.rag import rag
from pages.register import register

st.sidebar.title("Navigation")

if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    st.sidebar.write(f"Logged in as {st.session_state['username']}")

if st.session_state['page'] == 'login':
    login()
elif st.session_state['page'] == 'dashboard':
    dashboard()
elif st.session_state['page'] == 'rag':
    rag()
elif st.session_state['page'] == 'register':
    register()

if st.session_state['logged_in']:
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({'logged_in': False, 'username': '', 'page': 'login'}))
