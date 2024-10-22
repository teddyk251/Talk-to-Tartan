from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS

# Process data
def process_data(file_path: str, file_type:str):
    """
    Load data from a file for CSV anf directory for PDF and return a list of documents
    args:
    file_path: str: path to the file (CSV) or directory (PDF) to load
    file_type: str: type of file to load (csv or pdf)
    """
    if file_type == "csv":
        loader = CSVLoader(file_path=file_path, encoding='utf-8')
        documents = loader.load()
        print(f"""{len(documents)} documents loaded from {file_path}""")
    elif file_type == "pdf":
        loader = PyPDFDirectoryLoader(file_path)
        documents = loader.load()
        print(f"""{len(documents)} documents loaded from {file_path}""")
    else:
        raise ValueError("Invalid file type. Please provide a valid file type (csv or pdf)")
    return documents



# Create or load vector store
def initialize_vector_store(vector_store_path, data_file_path, embeddings, file_type):
    try:
        vector_store = FAISS.load_local(
            vector_store_path, embeddings, allow_dangerous_deserialization=True)
        print(f"Vector store loaded from {vector_store_path}")
    except:
        documents = process_data(data_file_path,file_type="pdf")
        vector_store = FAISS.from_documents(documents, embeddings)
        vector_store.save_local(vector_store_path)
        print(f"Vector store created and saved to {vector_store_path}")
    return vector_store
