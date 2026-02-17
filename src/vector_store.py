"""
Vector Store Module for ReportCheckAI.
Uses FAISS for local vector indexing and OpenAI for embeddings.
"""

import os
import faiss
import numpy as np
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class VectorIndex:
    def __init__(self, embedding_model="text-embedding-3-small"):
        self.model = embedding_model
        self.index = None
        self.documents = []  # To map index back to original text

    def get_embedding(self, text):
        """Generates a vector for the given text."""
        text = text.replace("\n", " ")
        return client.embeddings.create(input=[text], model=self.model).data[0].embedding

    def build_index(self, library):
        """
        Embeds the compliance rules and builds a FAISS index.
        """
        all_rules = []
        for filename, content in library["rules"].items():
            all_rules.append(content)

        if not all_rules:
            return

        self.documents = all_rules

        # 1. Generate embeddings
        embeddings = [self.get_embedding(rule) for rule in all_rules]
        embeddings_np = np.array(embeddings).astype('float32')

        # 2. Initialize FAISS index (using L2 distance)
        dimension = embeddings_np.shape[1]
        self.index = faiss.IndexFlatL2(dimension)

        # 3. Add vectors to the index
        self.index.add(embeddings_np)
        print(f"FAISS index built with {self.index.ntotal} rules.")

    def search(self, query, n_results=1):
        """Finds the most semantically similar rule for a query."""
        query_vector = np.array([self.get_embedding(query)]).astype('float32')
        distances, indices = self.index.search(query_vector, n_results)

        # Return the original text of the best match
        return [self.documents[i] for i in indices[0] if i != -1]


# Quick test logic
if __name__ == "__main__":
    from loader import load_all_documents

    # Setup paths
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lib = load_all_documents(os.path.join(project_root, "data"))

    # Initialize and Build
    v_store = VectorIndex()
    v_store.build_index(lib)

    # Test Search
    match = v_store.search("What is the rule for expert identity and contract ID?")
    print(f"\nTop Match found: {match[0][:100]}...")