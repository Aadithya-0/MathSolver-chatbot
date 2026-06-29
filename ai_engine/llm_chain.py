import os
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
embed_model="sentence-transformers/all-MiniLM-L6-v2"
faiss_path="ai_engine/faiss_index"
info_path="ai_engine/math_knowledge.txt"
def init_vector_store():
    print("loading knowledge base...")
    if not os.path.exists(info_path):
        raise FileNotFoundError(f"Ensure {info_path} exists")
    loader=TextLoader(info_path)
    documents=loader.load()
    print("chunking text")
    splitter=CharacterTextSplitter(chunk_size=200,chunk_overlap=50)
    docs=splitter.split_documents(documents)
    print("embedding texts and building faiss index...")
    embeddings=HuggingFaceEmbeddings(model_name=embed_model)
    vectorstore=FAISS.from_documents(docs,embeddings)
    vectorstore.save_local(faiss_path)
    print("FAISS saved successfully in ai_engine/faiss_index")
