
from ingestion.ingest_all import ingest_all_documents
from processing.chunker import split_documents
from processing.embeddings import create_embedding_model

from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever

from retrieval.hybrid_search import hybrid_search
from retrieval.reranker import load_reranker, rerank_documents


def main():

    query = "Why is IP 198.51.100.23 suspicious? Identify the targeted username and related events."

    print("\n========== RETRIEVAL DEBUG ==========")

    documents = ingest_all_documents()
    chunks = split_documents(documents)

    embedding_model = create_embedding_model()

    vector_store = Chroma(
        collection_name="cybershield_documents",
        embedding_function=embedding_model,
        persist_directory="vector_db/cybershield_chroma"
    )

    bm25_retriever = BM25Retriever.from_documents(
        chunks,
        k=5
    )

    hybrid_results = hybrid_search(
        query,
        vector_store,
        bm25_retriever
    )

    reranker = load_reranker()

    reranked_results = rerank_documents(
        query,
        hybrid_results,
        reranker
    )

    print("\n========== TOP RERANKED DOCUMENTS ==========")

    for index, (document, score) in enumerate(
        reranked_results,
        start=1
    ):

        print(f"\nRESULT {index}")
        print("Score:", round(score, 4))
        print("Source:", document.metadata.get("source"))

        print("\nFULL CONTENT:")
        print(document.page_content)

        print("\nMetadata:")
        print(document.metadata)

        print("------------------------------------")


if __name__ == "__main__":
    main()
