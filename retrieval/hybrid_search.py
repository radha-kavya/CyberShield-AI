
from langchain_community.retrievers import BM25Retriever
from langchain_chroma import Chroma

from ingestion.ingest_all import ingest_all_documents
from processing.chunker import split_documents
from processing.embeddings import create_embedding_model
from retrieval.query_transform import transform_query


CHROMA_DB_PATH = "vector_db/cybershield_chroma"
COLLECTION_NAME = "cybershield_documents"

TOP_K = 5


def reciprocal_rank_fusion(vector_results, keyword_results, k=60):

    combined_scores = {}
    documents = {}

    # 1. Vector search results
    for rank, document in enumerate(vector_results, start=1):

        doc_id = (
            document.metadata.get("source", "")
            + document.page_content
        )

        combined_scores[doc_id] = (
            combined_scores.get(doc_id, 0)
            + 1 / (k + rank)
        )

        documents[doc_id] = document

    # 2. BM25 keyword search results
    for rank, document in enumerate(keyword_results, start=1):

        doc_id = (
            document.metadata.get("source", "")
            + document.page_content
        )

        combined_scores[doc_id] = (
            combined_scores.get(doc_id, 0)
            + 1 / (k + rank)
        )

        documents[doc_id] = document

    # 3. Sort by combined RRF score
    ranked_ids = sorted(
        combined_scores,
        key=combined_scores.get,
        reverse=True
    )

    return [
        (documents[doc_id], combined_scores[doc_id])
        for doc_id in ranked_ids
    ]


def prioritize_exact_identifiers(query, results):

    """
    Give a relevance boost to documents containing
    exact IP addresses, usernames, and event IDs.
    """

    query_lower = query.lower()

    query_terms = query_lower.split()

    exact_identifiers = [
        term.strip(".,?!:;()[]{}")
        for term in query_terms
        if (
            term.startswith("net")
            or term.count(".") == 3
        )
    ]

    if not exact_identifiers:
        return results

    boosted_results = []

    for document, score in results:

        content = document.page_content.lower()

        boost = 0

        for identifier in exact_identifiers:

            if identifier in content:
                boost += 0.05

        boosted_results.append(
            (document, score + boost)
        )

    return sorted(
        boosted_results,
        key=lambda item: item[1],
        reverse=True
    )


def remove_duplicate_chunks(results):

    """
    Remove exact duplicate document chunks.
    Keep the highest-ranked occurrence.
    """

    unique_results = []
    seen = set()

    for document, score in results:

        doc_id = (
            document.metadata.get("source", "")
            + document.page_content
        )

        if doc_id not in seen:

            seen.add(doc_id)

            unique_results.append(
                (document, score)
            )

    return unique_results


def hybrid_search(query, vector_store, bm25_retriever):

    # 1. Transform query
    transformed_query = transform_query(query)

    print("\nOriginal Query:")
    print(query)

    print("\nTransformed Query:")
    print(transformed_query)

    # 2. Vector search
    vector_results = vector_store.similarity_search(
        transformed_query,
        k=TOP_K
    )

    # 3. BM25 keyword search
    keyword_results = bm25_retriever.invoke(
        transformed_query
    )

    # 4. Reciprocal Rank Fusion
    results = reciprocal_rank_fusion(
        vector_results,
        keyword_results
    )

    # 5. Prioritize exact identifiers from original query
    results = prioritize_exact_identifiers(
        query,
        results
    )

    # 6. Remove duplicate chunks
    results = remove_duplicate_chunks(results)

    # 7. Return top results
    return results[:TOP_K]


if __name__ == "__main__":

    print("\nLoading CyberShield AI documents...")

    documents = ingest_all_documents()

    chunks = split_documents(documents)

    print("\nTotal Documents:", len(documents))
    print("Total Chunks:", len(chunks))

    embedding_model = create_embedding_model()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=CHROMA_DB_PATH
    )

    print("Stored Vectors:", vector_store._collection.count())

    bm25_retriever = BM25Retriever.from_documents(
        chunks,
        k=TOP_K
    )

    query = "What was the related network event NET001?"

    results = hybrid_search(
        query,
        vector_store,
        bm25_retriever
    )

    print("\n========== CYBERSHIELD AI ==========")
    print("           HYBRID SEARCH")
    print("====================================")

    for index, (document, score) in enumerate(results, start=1):

        print(f"\nResult {index}")

        print("Content:")
        print(document.page_content[:400])

        print("\nSource:")
        print(document.metadata.get("source"))

        print("\nMetadata:")
        print(document.metadata)

        print("RRF Score:", round(score, 5))

        print("------------------------------------")

    print("\nHybrid search completed!")
