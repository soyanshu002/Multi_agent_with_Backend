from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_and_chunk(file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """Load PDF or CSV and split into chunks"""

    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".csv"):
        loader = CSVLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

    documents = loader.load()

    # add source metadata to each chunk
    for doc in documents:
        doc.metadata["source"] = file_path

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = splitter.split_documents(documents)
    return chunks