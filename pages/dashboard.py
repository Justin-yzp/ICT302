import streamlit as st
from datetime import date


def dashboard():
    st.title("Dashboard")

    st.write(f"Welcome, {st.session_state['username']}!")

    st.write("## Calendar")
    selected_date = st.date_input("Select a date", date.today())
    st.write("Selected date:", selected_date)

    if st.button("RAG Retrieval Augmented Generation"):
        st.session_state['page'] = 'rag'

    st.sidebar.write(f"Logged in as {st.session_state['username']}")
