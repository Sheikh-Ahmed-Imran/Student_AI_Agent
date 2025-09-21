import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI # ✅ Correct import

# Embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load FAISS
vectorstore = FAISS.load_local(
    "campus_faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

# Google Gemini LLM
key = "AIzaSyDX71TefE9O94kL4jQJF9s-UMbsVpxOc5Y"
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=key,
    streaming=False
)

# RAG chain
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    chain_type="stuff"
)




