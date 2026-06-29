from httpx import __name
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
def get_retriever():
    embeddings=HuggingFaceEmbeddings(model_name=embed_model)
    if not os.path.exists(faiss_path):
        print("FAISS index not found,building it")
        init_vector_store()
    vectorstore=FAISS.load_local(faiss_path,embeddings,allow_dangerous_deserialization=True)
    return vectorstore.as_retriever(search_kwargs={"k":2})
if __name__ == "__main__":
    init_vector_store()