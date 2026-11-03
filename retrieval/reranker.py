
from sentence_transformers import CrossEncoder
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever

from ingestion.ingest_all import ingest_all_documents
from processing.chunker import split_documents
from processing.embeddings import create_embedding_model
from retrieval.hybrid_search import hybrid_search


CHROMA_DB_PATH = "vector_db/cybershield_chroma"
COLLECTION_NAME = "cybershield_documents"

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def load_reranker():

    print("\nLoading Cross-Encoder model...")

    reranker = CrossEncoder(
        RERANKER_MODEL
    )

    return reranker


def rerank_documents(query, documents, reranker):

    # Create query-document pairs
    pairs = [
        [query, document.page_content]
        for document, _ in documents
    ]

    # Calculate relevance scores
    scores = reranker.predict(pairs)

    # Combine documents and scores
    ranked_documents = []

    for (document, _), score in zip(documents, scores):

        ranked_documents.append(
            (document, float(score))
        )

    # Sort by relevance score
    ranked_documents.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return ranked_documents


if __name__ == "__main__":

    # 1. Load documents
    documents = ingest_all_documents()

    # 2. Create chunks
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

    print("Stored Vectors:", vector_store._collection.count())

    # 5. Create BM25 retriever
    bm25_retriever = BM25Retriever.from_documents(
        chunks,
        k=5
    )

    # 6. User query
    query = "Repeated failed login attempts from 198.51.100.23"

    # 7. Perform hybrid search
    hybrid_results = hybrid_search(
        query,
        vector_store,
        bm25_retriever
    )

    print("\nHybrid Search Results:", len(hybrid_results))

    # 8. Load Cross-Encoder
    reranker = load_reranker()

    # 9. Rerank retrieved documents
    reranked_results = rerank_documents(
        query,
        hybrid_results,
        reranker
    )

    # 10. Display final results
    print("\n========== CYBERSHIELD AI ==========")
    print("       CROSS-ENCODER RERANKING")
    print("====================================")

    print("\nSearch Query:")
    print(query)

    print("\nReranked Documents:")

    for index, (document, score) in enumerate(
        reranked_results, start=1
    ):

        print(f"\nRank: {index}")

        print("Relevance Score:", round(score, 4))

        print("\nContent:")
        print(document.page_content[:400])

        print("\nSource:")
        print(document.metadata.get("source"))

        print("\nMetadata:")
        print(document.metadata)

        print("------------------------------------")

    print("\n====================================")
    print("Cross-Encoder reranking completed successfully!")
