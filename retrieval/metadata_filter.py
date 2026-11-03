
from langchain_chroma import Chroma

from processing.embeddings import create_embedding_model


CHROMA_DB_PATH = "vector_db/cybershield_chroma"
COLLECTION_NAME = "cybershield_documents"


def create_chroma_store():

    embedding_model = create_embedding_model()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=CHROMA_DB_PATH
    )

    return vector_store


def metadata_search(
    vector_store,
    query,
    severity=None,
    event_type=None,
    source_ip=None
):

    # Build metadata filter
    conditions = []

    if severity:
        conditions.append({"severity": severity})

    if event_type:
        conditions.append({"event_type": event_type})

    if source_ip:
        conditions.append({"source_ip": source_ip})

    # Combine multiple conditions using AND
    if len(conditions) == 1:
        metadata_filter = conditions[0]

    elif len(conditions) > 1:
        metadata_filter = {"$and": conditions}

    else:
        metadata_filter = None

    # Search ChromaDB
    if metadata_filter:
        results = vector_store.similarity_search(
            query,
            k=5,
            filter=metadata_filter
        )
    else:
        results = vector_store.similarity_search(
            query,
            k=5
        )

    return results


if __name__ == "__main__":

    print("\nLoading CyberShield AI metadata search...")

    # Connect to existing ChromaDB
    vector_store = create_chroma_store()

    print("\nStored Vectors:", vector_store._collection.count())

    # Test query
    query = "Find suspicious network security events"

    results = metadata_search(
        vector_store=vector_store,
        query=query,
        severity="high"
    )

    print("\n========== CYBERSHIELD AI ==========")
    print("          METADATA FILTERING")
    print("====================================")

    print("\nSearch Query:", query)
    print("Severity Filter: high")

    print("\nFiltered Documents:")

    for index, document in enumerate(results, start=1):

        print(f"\nResult {index}")

        print("Content:")
        print(document.page_content[:400])

        print("\nSource:")
        print(document.metadata.get("source"))

        print("\nMetadata:")
        print(document.metadata)

        print("------------------------------------")

    print("\n====================================")
    print("Metadata filtering completed successfully!")
