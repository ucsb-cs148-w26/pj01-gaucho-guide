import os
import time
import json
from typing import List, Any
import hashlib

import click
from dotenv import load_dotenv
try:
    # Preferred path for newer LangChain split packages.
    from langchain_classic.chains.query_constructor.schema import AttributeInfo
    from langchain_classic.retrievers import SelfQueryRetriever
except ImportError:
    # Backward-compatible path for older LangChain installs.
    from langchain.chains.query_constructor.schema import AttributeInfo
    from langchain.retrievers import SelfQueryRetriever
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec

from src.llm.llmswap import getLLM
from src.models.query_route import RouteQuery

load_dotenv()
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-3-flash-preview")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
GEMINI_EMBEDDING_DIMENSION = int(os.getenv("GEMINI_EMBEDDING_DIMENSION", "3072"))
SCHEMA_FILE = os.getenv("SCHEMA_FILE", "namespace_schemas.json")


def _normalize_text_content(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(str(item.get("text", "")))
            elif isinstance(item, str):
                text_parts.append(item)
        return "\n".join(part for part in text_parts if part).strip()

    return str(content).strip()


class VectorManager:
    def __init__(self, api_key):
        self.pc = Pinecone(api_key=api_key)
        self.embeddings = GoogleGenerativeAIEmbeddings(model=GEMINI_EMBEDDING_MODEL)
        self.llm = getLLM(provider="gemini", model_name=GEMINI_MODEL_NAME, temperature=0)

        existing_indexes = [i.name for i in self.pc.list_indexes()]
        if PINECONE_INDEX_NAME not in existing_indexes:
            click.secho(f"Creating Pinecone Index '{PINECONE_INDEX_NAME}'...", fg="yellow")
            self.pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=GEMINI_EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            time.sleep(2)
        else:
            index_info = self.pc.describe_index(name=PINECONE_INDEX_NAME)
            existing_dimension = index_info.dimension
            if existing_dimension != GEMINI_EMBEDDING_DIMENSION:
                raise ValueError(
                    "Pinecone index dimension mismatch. "
                    f"Index '{PINECONE_INDEX_NAME}' has dimension {existing_dimension}, "
                    f"but Gemini embeddings use {GEMINI_EMBEDDING_DIMENSION}. "
                    "Use a new PINECONE_INDEX_NAME or recreate this index with the Gemini dimension."
                )

        self.vector_store = PineconeVectorStore(
            index_name=PINECONE_INDEX_NAME,
            embedding=self.embeddings
        )

    def _generate_field_description(self, key: str, sample_value: Any) -> str:
        """
        Asks the LLM to explain what a metadata field means based on its name and a sample.
        """
        prompt = (
            f"I have a dataset column named '{key}'. "
            f"A sample value is: '{sample_value}'. "
            "Write a very concise description (max 10 words) of what this field represents. "
            "Return ONLY the description, no other text."
        )
        response = self.llm.invoke(prompt)
        description = _normalize_text_content(response.content)
        return description

    def _infer_and_save_schema(self, documents: List[Document], namespace: str):
        """
        Scans docs, detects fields, asks LLM for descriptions, and saves schema.
        """
        if os.path.exists(SCHEMA_FILE):
            with open(SCHEMA_FILE, "r") as f:
                registry = json.load(f)
        else:
            registry = {}

        current_schema = {item['name']: item for item in registry.get(namespace, [])}

        updated = False

        for doc in documents:
            for key, value in doc.metadata.items():
                if key not in current_schema:
                    click.secho(f"   ...Detecting new field '{key}'. Generating description...", fg="cyan")

                    type_name = "string"
                    if isinstance(value, float):
                        type_name = "float"
                    elif isinstance(value, int):
                        type_name = "integer"

                    description = self._generate_field_description(key, value)

                    current_schema[key] = {
                        "name": key,
                        "description": description,
                        "type": type_name
                    }
                    updated = True

        if updated:
            registry[namespace] = list(current_schema.values())
            with open(SCHEMA_FILE, "w") as f:
                json.dump(registry, f, indent=2)
            click.secho(f"Schema for '{namespace}' updated with AI descriptions.", fg="green")
        else:
            print(f"No new schema fields detected for {namespace}.")

    def ingest_data(self, documents: List[Document], namespace: str):
        if not documents:
            return

        ids = []
        for doc in documents:
            content_bytes = doc.page_content.encode('utf-8')
            doc_hash = hashlib.md5(content_bytes).hexdigest()
            ids.append(doc_hash)
        click.secho(f"Embedding and storing {len(documents)} reviews into Pinecone...", fg="yellow")
        self._infer_and_save_schema(documents, namespace)
        self.vector_store.add_documents(documents=documents,
                                        ids=ids,
                                        namespace=namespace)
        click.secho("Ingestion Complete!", fg="green")

    def route_query(self, query: str) -> str:
        structured_llm = self.llm.with_structured_output(RouteQuery)
        try:
            result = structured_llm.invoke(query)
            print(f"[namespace]: {result.namespace}")
            return result.namespace

        except Exception as e:
            print(f"Routing failed ({e}), defaulting to Professor data.")
            return "professor_data"

    def search(self, query: str, k=5):
        """
        Dynamically loads schema and performs self-querying search.
        """
        namespace = self.route_query(query)

        if not os.path.exists(SCHEMA_FILE):
            return self.vector_store.similarity_search(query, k=k, namespace=namespace)

        with open(SCHEMA_FILE, "r") as f:
            registry = json.load(f)

        if namespace not in registry:
            return self.vector_store.similarity_search(query, k=k, namespace=namespace)

        schema_data = registry[namespace]
        metadata_field_info = [
            AttributeInfo(
                name=item["name"],
                description=item["description"],
                type=item["type"]
            ) for item in schema_data
        ]

        retriever = SelfQueryRetriever.from_llm(
            llm=self.llm,
            vectorstore=self.vector_store,
            document_contents=f"Data entries for {namespace}",
            metadata_field_info=metadata_field_info,
            verbose=True,
            search_kwargs={"namespace": namespace, "k": k}
        )

        try:
            return retriever.invoke(query)
        except Exception as e:
            click.secho(f"Self-query failed, falling back to basic search: {e}", fg="red")
            return self.vector_store.similarity_search(query, k=k, namespace=namespace)

    def std_search(self, query: str, k=5):
        """
        Performs standard similarity search within a routed namespace.
        """
        namespace = self.route_query(query)

        try:
            results = self.vector_store.similarity_search(
                query=query,
                k=k,
                namespace=namespace
            )
            return results

        except Exception as e:
            click.secho(f"Search in namespace '{namespace}' failed: {e}", fg="red")
            return self.vector_store.similarity_search(query, k=k)
