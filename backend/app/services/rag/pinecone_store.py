from langchain_community.embeddings import JinaEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings
from dotenv import load_dotenv
load_dotenv()
import os

# ← ADD THIS to debug
print("EMBEDDING_MODEL:", settings.EMBEDDING_MODEL)
print("EMBEDDING_DIMENSION:", settings.EMBEDDING_DIMENSION)
print("PINECONE_KEY:", settings.PINECONE_API_KEY[:10], "...")


def get_pinecone_client() -> Pinecone:
    return Pinecone(api_key=settings.PINECONE_API_KEY)


def ensure_index_exists():
    pc = get_pinecone_client()
    if settings.PINECONE_INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=settings.PINECONE_INDEX_NAME,
            dimension=768,          # ← HARDCODED to match existing index
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )


def get_embeddings():
    return JinaEmbeddings(
        model_name="jina-embeddings-v2-base-en",   # ← HARDCODED 768 dims
        jina_api_key=settings.JINA_API_KEY
    )


def create_vector_store(chunks, namespace: str) -> PineconeVectorStore:
    ensure_index_exists()
    vector_store = PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        index_name=settings.PINECONE_INDEX_NAME,
        namespace=namespace
    )
    return vector_store


def get_vector_store(namespace: str) -> PineconeVectorStore:
    ensure_index_exists()
    return PineconeVectorStore(
        index_name=settings.PINECONE_INDEX_NAME,
        embedding=get_embeddings(),
        namespace=namespace
    )


def similarity_search(query: str, namespace: str, k: int = 4) -> list:
    store = get_vector_store(namespace)
    return store.similarity_search(query, k=k)


def delete_namespace(namespace: str):
    pc = get_pinecone_client()
    index = pc.Index(settings.PINECONE_INDEX_NAME)
    index.delete(delete_all=True, namespace=namespace)