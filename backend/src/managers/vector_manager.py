import time
from typing import List

import click
from langchain_ollama import OllamaEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec

PINECONE_INDEX_NAME = "ucsb-gaucho-index"
MODEL_NAME = "llama3.1"


class VectorManager:
    def __init__(self, api_key):
        self.pc = Pinecone(api_key=api_key)
        self.embeddings = OllamaEmbeddings(model=MODEL_NAME)

        existing_indexes = [i.name for i in self.pc.list_indexes()]
        if PINECONE_INDEX_NAME not in existing_indexes:
            click.secho(f"Creating Pinecone Index '{PINECONE_INDEX_NAME}'...", fg="yellow")
            self.pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=4096,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            time.sleep(2)

        self.vector_store = PineconeVectorStore(
            index_name=PINECONE_INDEX_NAME,
            embedding=self.embeddings
        )

    def ingest_data(self, documents: List[Document]):
        if not documents:
            return
        click.secho(f"Embedding and storing {len(documents)} reviews into Pinecone...", fg="yellow")
        self.vector_store.add_documents(documents)
        click.secho("Ingestion Complete!", fg="green")

    def search(self, query: str, k=5):
        return self.vector_store.similarity_search(query, k=k)
