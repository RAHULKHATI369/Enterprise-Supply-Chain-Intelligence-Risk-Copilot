import os
from typing import List, Any, Dict, Optional, cast

import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

SLA_TXT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "vendor_sla_policy.txt")

class RAGAgent:
    def __init__(self) -> None:
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.get_or_create_collection(name="sla_policies")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.llm: Optional[Any] = None

        if self.api_key:
            # Pylance-safe resolution for google.generativeai exports
            configure_fn = getattr(genai, "configure", None)
            model_cls = getattr(genai, "GenerativeModel", None)

            if configure_fn and model_cls:
                configure_fn(api_key=self.api_key)
                self.llm = model_cls('gemini-1.5-flash')

        self._ingest_documents()

    def _ingest_documents(self) -> None:
        """Chunk and index vendor SLA policy into vector DB."""
        if not os.path.exists(SLA_TXT_PATH):
            return

        with open(SLA_TXT_PATH, "r", encoding="utf-8") as f:
            text = f.read()

        # Simple semantic chunking by sections
        chunks: List[str] = [c.strip() for c in text.split("\n\n") if c.strip()]
        
        # Explicit type-casting for ChromaDB Pylance signatures
        raw_embeddings = self.embedder.encode(chunks)
        embeddings_list: List[List[float]] = cast(List[List[float]], raw_embeddings.tolist())
        
        ids: List[str] = [f"chunk_{i}" for i in range(len(chunks))]
        metadatas: List[Dict[str, str]] = [{"source": "vendor_sla_policy.txt"} for _ in chunks]

        self.collection.add(
            documents=chunks,
            embeddings=cast(Any, embeddings_list),
            ids=ids,
            metadatas=cast(Any, metadatas)
        )

    def query_sla_policy(self, query_text: str) -> Dict[str, Any]:
        """Retrieves contexts and generates an answer grounded in SLA policy."""
        raw_query_emb = self.embedder.encode([query_text])
        query_emb_list: List[List[float]] = cast(List[List[float]], raw_query_emb.tolist())

        results = self.collection.query(
            query_embeddings=cast(Any, query_emb_list), 
            n_results=2
        )

        retrieved_docs: List[str] = results['documents'][0] if results and results['documents'] else []
        context: str = "\n---\n".join(retrieved_docs)

        if not self.llm:
            return {
                "answer": f"[Mock RAG Response - Set GEMINI_API_KEY for LLM generation]\nRetrieved Context Excerpt:\n{context}",
                "sources": ["vendor_sla_policy.txt"]
            }

        prompt = f"""
        You are an Enterprise Supply Chain Legal & SLA Assistant.
        Answer the following query using ONLY the provided context excerpts from the vendor SLA policy.
        If the answer is not contained in the context, state that explicitly.

        Context Excerpts:
        {context}

        Question: {query_text}
        Answer:
        """
        try:
            response = self.llm.generate_content(prompt)
            return {"answer": response.text.strip(), "sources": ["vendor_sla_policy.txt"]}
        except Exception as e:
            return {"answer": f"Error running RAG LLM pipeline: {str(e)}", "sources": []}