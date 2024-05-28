from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import base64
from process_pdfs.process_pdfs import process_pdfs
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

def handle_userinput(user_question):
    if 'conversation' in st.session_state:
        response = st.session_state.conversation({'question': user_question})
        st.session_state.chat_history = response['chat_history']

        for message in reversed(st.session_state.chat_history):
            metadata = getattr(message, 'metadata', {})  # Use getattr to safely get metadata
            source = metadata.get('source', 'Unknown')
            if source != 'Unknown':
                st.write(f"## Source: {source}")

            st.write("## AI Response")
            formatted_message = bot_template.replace("{{MSG}}", message.content)
            st.write(formatted_message, unsafe_allow_html=True)

    else:
        st.error("Conversation chain is not initialized. Please process the PDFs first.")

def rag():
    st.title("RAG Retrieval Augmented Generation")
    user_question = st.text_input("Ask a question:")
    if user_question:
        handle_userinput(user_question)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    if st.session_state.conversation is None:
        st.subheader("Processing PDFs")
        with st.spinner("Loading and processing PDFs..."):
            vectorstore = process_pdfs()
            st.session_state.conversation = get_conversation_chain(vectorstore)
        st.success("PDFs processed successfully. You can now ask questions.")

    if st.button("Back to Dashboard"):
        st.session_state['page'] = 'dashboard'

if __name__ == '__main__':
    rag()
