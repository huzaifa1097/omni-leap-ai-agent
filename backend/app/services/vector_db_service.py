import chromadb
from sentence_transformers import SentenceTransformer
import uuid

# This creates a persistent client that saves data to disk in a 'chroma_db' directory.
client = chromadb.PersistentClient(path="./chroma_db")

# This model runs locally on your machine to turn text into vectors.
print("Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Embedding model loaded.")

def add_text_to_vector_db(user_id: str, text: str, metadata: dict):
    """
    Creates an embedding for a piece of text and stores it in a user-specific collection.
    """
    try:
        # --- THIS IS THE FIX ---
        # Get or create a collection named specifically for the user (e.g., "user_RYXUt8...")
        # This ensures each user has their own private memory.
        collection = client.get_or_create_collection(name=f"user_{user_id}")
        
        embedding = embedding_model.encode(text).tolist()
        
        collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata],
            ids=[str(uuid.uuid4())]
        )
        print(f"Successfully added text to vector DB for user {user_id}")

    except Exception as e:
        print(f"Error adding text to vector DB for user {user_id}: {e}")


def search_user_memory(user_id: str, query_text: str, n_results: int = 3) -> list:
    """
    Searches a user's memory for the most relevant past conversations.
    """
    try:
        # --- THIS IS THE FIX ---
        # We now get the specific collection for the user, ensuring we only search their memories.
        collection = client.get_collection(name=f"user_{user_id}")
        
        query_embedding = embedding_model.encode(query_text).tolist()
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return results.get('documents', [[]])[0]

    except Exception as e:
        # This is expected if the user has no history yet.
        print(f"Could not search memory for user {user_id} (collection might not exist yet): {e}")
        return []
