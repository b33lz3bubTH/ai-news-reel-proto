# chroma_client.py
import chromadb
import os

home_dir = os.path.expanduser("~")

class ChromaConfig:
    CHROMA_DB_PATH = os.path.join(home_dir, 'chroma.vecdb')
    COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "default_collection")

class ChromaClient:
    """Singleton client for managing ChromaDB connection."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaClient, cls).__new__(cls)
            cls._instance.client = chromadb.PersistentClient(path=ChromaConfig.CHROMA_DB_PATH)
        return cls._instance

    def get_or_create_collection(self, collection_name: str = ChromaConfig.COLLECTION_NAME):
        """Get or create a collection."""
        return self.client.get_or_create_collection(collection_name)
