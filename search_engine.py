import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pickle

class SearchEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        print("Loading Search Engine Model...")
        self.model = SentenceTransformer(model_name)
        self.dimension = 384 # Dimension for MiniLM-L6-v2
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = [] # Keep track of document IDs corresponding to index
        
    def encode(self, text):
        return self.model.encode([text])[0]
    
    def bulk_encode(self, texts):
        return self.model.encode(texts)
    
    def add_document(self, doc_id, text, embedding=None):
        if embedding is None:
            embedding = self.encode(text)
            
        # Add to FAISS index
        # FAISS expects float32 numpy array
        vector = np.array([embedding]).astype('float32')
        self.index.add(vector)
        self.documents.append(doc_id)
        
        return embedding
        
    def search(self, query, k=5):
        query_vector = self.encode(query)
        query_vector = np.array([query_vector]).astype('float32')
        
        distances, indices = self.index.search(query_vector, k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1 and idx < len(self.documents):
                doc_id = self.documents[idx]
                results.append((doc_id, float(distances[0][i])))
                
        return results

    def find_similar(self, doc_id, k=5):
        """Find papers similar to the given doc_id."""
        if doc_id not in self.documents:
            return []
            
        # Find index of doc_id in our list
        idx = self.documents.index(doc_id)
        
        # Reconstruct vector (FAISS IndexFlatL2 doesn't support get_vector easily unless using reconstruct if mapped)
        # But we stored it in DB. Let's assume we can re-encode or we should have kept vectors in memory.
        # Issue: efficient search needs vector. 
        # Hack for now: use the index's reconstruct() if available or just re-encode abstract?
        # Better: We have the vector in the FAISS index. IndexFlatL2 supports `reconstruct(i)`.
        
        try:
            vector = self.index.reconstruct(idx)
            vector = np.array([vector]).astype('float32')
            
            # Search k+1 because the doc itself will be the top result (distance 0)
            distances, indices = self.index.search(vector, k+1)
            
            results = []
            for i in range(len(indices[0])):
                result_idx = indices[0][i]
                if result_idx != -1 and result_idx < len(self.documents):
                    result_doc_id = self.documents[result_idx]
                    if result_doc_id != doc_id: # Exclude self
                        results.append((result_doc_id, float(distances[0][i])))
                        
            return results[:k]
        except Exception as e:
            print(f"Error finding similar docs: {e}")
            return []

    def rebuild_index(self, documents):
        """
        Rebuilds index from a list of Document objects.
        Expected documents to have 'id', 'abstract', and optionally 'embedding'.
        """
        print(f"Rebuilding index for {len(documents)} documents...")
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        
        texts_to_encode = []
        docs_to_update = []
        
        for doc in documents:
            if doc.embedding:
                self.add_document(doc.id, doc.abstract, pickle.loads(doc.embedding))
            else:
                texts_to_encode.append(doc.abstract)
                docs_to_update.append(doc)
                
        # Bulk encode missing embeddings
        if texts_to_encode:
            print(f"Generating embeddings for {len(texts_to_encode)} new documents...")
            embeddings = self.bulk_encode(texts_to_encode)
            for i, doc in enumerate(docs_to_update):
                # Save back to doc object (caller needs to commit to DB)
                header_embedding = embeddings[i]
                self.add_document(doc.id, doc.abstract, header_embedding)
                doc.embedding = pickle.dumps(header_embedding)
