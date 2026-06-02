"""
Vector Store Module for ReportCheckAI.
Uses FAISS for local vector indexing and OpenAI for embeddings.
"""

import json
import os

import faiss
import numpy as np
from openai import OpenAI

from src.config import EMBEDDING_MODEL, FAISS_DOCS_PATH, FAISS_INDEX_PATH


class VectorIndex:
    def __init__(self, embedding_model=EMBEDDING_MODEL, client=None):
        self.model = embedding_model
        self.index = None
        self.documents = []
        self.client = client or OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_embeddings_batch(self, texts):
        texts = [t.replace("\n", " ") for t in texts]
        response = self.client.embeddings.create(input=texts, model=self.model)
        return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]

    def _chunk_text(self, text, min_length=60):
        """Split a document into paragraph-level chunks, discarding very short ones."""
        chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) >= min_length]
        return chunks if chunks else [text]

    def build_index(self, library, index_path=FAISS_INDEX_PATH, docs_path=FAISS_DOCS_PATH):
        """Embeds each rule chunk individually and builds a FAISS index."""
        all_chunks = []
        for content in library["rules"].values():
            if content:
                all_chunks.extend(self._chunk_text(content))

        if not all_chunks:
            return

        self.documents = all_chunks

        embeddings = self.get_embeddings_batch(all_chunks)
        embeddings_np = np.array(embeddings).astype("float32")

        dimension = embeddings_np.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings_np)

        self.save(index_path, docs_path)
        print(f"FAISS index built with {self.index.ntotal} rule chunks.")

    def search(self, query, n_results=2):
        """Returns the top-n most semantically similar rule chunks for a query."""
        query_vector = np.array(self.get_embeddings_batch([query])).astype("float32")
        distances, indices = self.index.search(query_vector, n_results)
        return [self.documents[i] for i in indices[0] if i != -1]

    def save(self, index_path=FAISS_INDEX_PATH, docs_path=FAISS_DOCS_PATH):
        faiss.write_index(self.index, index_path)
        with open(docs_path, "w") as f:
            json.dump(self.documents, f)

    def load(self, index_path=FAISS_INDEX_PATH, docs_path=FAISS_DOCS_PATH):
        """Loads a previously saved FAISS index from disk. Returns True on success."""
        if not os.path.exists(index_path) or not os.path.exists(docs_path):
            return False
        self.index = faiss.read_index(index_path)
        with open(docs_path) as f:
            self.documents = json.load(f)
        return True


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    from src.loader import load_all_documents

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lib = load_all_documents(os.path.join(project_root, "data"))

    v_store = VectorIndex()
    v_store.build_index(lib)

    match = v_store.search("What is the rule for expert identity and contract ID?")
    print(f"\nTop match: {match[0][:200]}...")
