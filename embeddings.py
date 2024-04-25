import streamlit as st

from openai import OpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.llms import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

pdf_folder = 'pdfs'
pdf_files = [os.path.join(pdf_folder, file) for file in os.listdir(pdf_folder) if file.endswith('.pdf')]

loaders = [PyPDFLoader(pdf_file) for pdf_file in pdf_files]

docs = []

for file in loaders:
    docs.extend(file.load())

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(docs)
embedding_function = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device': 'cpu'})

vector_store = Chroma.from_documents(docs, embedding_function, persist_directory='./chroma_db_nccn')

print(vector_store._collection.count())