import os
import streamlit as st
import base64
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template

# Load environment variables
load_dotenv()

def load_pdfs_from_folder(folder_path='pdfs'):
    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.pdf')]
    text_data = []
    for pdf_file in pdf_files:
        try:
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            text_data.append((os.path.basename(pdf_file), text))
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
    return text_data

def get_text_chunks(text_data):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = []
    for source, text in text_data:
        split_texts = text_splitter.split_text(text)
        for chunk in split_texts:
            metadata = {'source': source}  # Set metadata for each chunk
            chunks.append((metadata, chunk))
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    texts = [chunk for _, chunk in text_chunks]
    metadata = [{'source': source} for source, _ in text_chunks]
    vectorstore = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadata)
    return vectorstore

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

        left_panel, right_panel = st.columns(2)

        with left_panel:
            st.write("## Relevant PDFs and Excerpts")
            for message in reversed(st.session_state.chat_history):
                if hasattr(message, 'metadata'):
                    metadata = message.metadata
                    source = metadata.get('source', 'Unknown')
                    if source != 'Unknown':
                        st.write(f"**Source:** {source}")
                        # Add a download button for the PDF
                        pdf_base64 = base64.b64encode(message.content.encode()).decode()
                        st.download_button(f"Download {source}", data=message.content, file_name=f"{source}.pdf")

                    st.write(f"**Content:** {message.content}")

        with right_panel:
            st.write("## AI Response")
            for i, message in enumerate(reversed(st.session_state.chat_history)):
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
            text_data = load_pdfs_from_folder()
            text_chunks = get_text_chunks(text_data)
            vectorstore = get_vectorstore(text_chunks)
            st.session_state.conversation = get_conversation_chain(vectorstore)
        st.success("PDFs processed successfully. You can now ask questions.")

    if st.button("Back to Dashboard"):
        st.session_state['page'] = 'dashboard'
