import os
import pickle
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def process_pdfs(folder_path='pdfs', cache_path='vectorstore_cache.pkl'):
    # Check if API key is loaded
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error("OpenAI API key not found. Make sure it is set in the environment variables.")
        return None

    if os.path.exists(cache_path):
        with open(cache_path, 'rb') as f:
            return pickle.load(f)

    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.pdf')]
    text_data = []
    for pdf_file in pdf_files:
        try:
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                text += page.extract_text()
                text_data.append((os.path.basename(pdf_file), text, page_num))
        except Exception as e:
            st.error(f"Error reading PDF: {e}")

    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len)
    chunks = []
    chunk_id = 0
    for source, text, page_num in text_data:
        split_texts = text_splitter.split_text(text)
        for chunk in split_texts:
            metadata = {
                'source': source,
                'chunk': chunk_id,
                'page_number': page_num
            }
            chunks.append((metadata, chunk))
            chunk_id += 1

    embeddings = OpenAIEmbeddings()  # The API key will be picked up from the environment variable
    texts = [chunk for _, chunk in chunks]
    metadatas = [metadata for metadata, _ in chunks]
    vectorstore = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)

    with open(cache_path, 'wb') as f:
        pickle.dump(vectorstore, f)

    return vectorstore
