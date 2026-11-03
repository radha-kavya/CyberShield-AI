
from langchain_chroma import Chroma

from processing.chunker import split_documents
from processing.embeddings import create_embedding_model
from ingestion.ingest_all import ingest_all_documents


# ChromaDB configuration
CHROMA_DB_PATH = "vector_db/cybershield_chroma"
COLLECTION_NAME = "cybershield_documents"


def create_vector_store():

    print("\nLoading documents...")

    # 1. Load all documents
    documents = ingest_all_documents()

    # 2. Apply advanced chunking
    chunks = split_documents(documents)

    print("\nTotal Documents:", len(documents))
    print("Total Chunks:", len(chunks))

    # 3. Load embedding model
    embedding_model = create_embedding_model()

    # 4. Connect to ChromaDB
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=CHROMA_DB_PATH
    )

    # 5. Delete old collection contents
    old_count = vector_store._collection.count()

    if old_count > 0:

        print("\nRemoving old vectors:", old_count)

        vector_store.delete_collection()

        # Recreate an empty collection
        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embedding_model,
            persist_directory=CHROMA_DB_PATH
        )

    # 6. Store newly generated chunks
    if chunks:

        vector_store.add_documents(chunks)

    # 7. Verify stored vectors
    stored_count = vector_store._collection.count()

    print("\nNew vectors stored:", stored_count)

    return vector_store, chunks


if __name__ == "__main__":

    vector_store, chunks = create_vector_store()

    # 8. Test semantic similarity search
    query = "Repeated failed login attempts from suspicious IP addresses"

    print("\n========== CYBERSHIELD AI ==========")
    print("        CHROMADB VECTOR STORE")
    print("====================================")

    print("\nCollection Name:", COLLECTION_NAME)
    print("Stored Vectors:", vector_store._collection.count())

    print("\nSearch Query:")
    print(query)

    results = vector_store.similarity_search(
        query,
        k=3
    )

    print("\nRetrieved Documents:")

    for index, document in enumerate(results, start=1):

        print(f"\nResult {index}")

        print("Content:")
        print(document.page_content[:300])

        print("\nMetadata:")
        print(document.metadata)

        print("------------------------------------")

    print("\n====================================")
    print("ChromaDB rebuilt successfully!")

