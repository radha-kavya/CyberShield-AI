
import re
import time

from langchain_community.retrievers import BM25Retriever

from retrieval.vector_store import create_vector_store
from retrieval.hybrid_search import hybrid_search
from retrieval.reranker import load_reranker, rerank_documents

from rag.answer_generator import generate_answer


# -----------------------------------------
# EVALUATION TEST DATASET
# -----------------------------------------

TEST_CASES = [
    {
        "question": "Why is IP 198.51.100.23 suspicious?",
        "expected_facts": [
            "198.51.100.23",
            "failed login",
            "john",
            "NET001"
        ],
        "retrieval_keywords": [
            "198.51.100.23",
            "failed login",
            "incident"
        ],
        "relevance_keywords": [
            "suspicious",
            "failed login",
            "connection",
            "investigation"
        ]
    },
    {
        "question": (
            "Which account was targeted by IP 198.51.100.23?"
        ),
        "expected_facts": [
            "john",
            "198.51.100.23"
        ],
        "retrieval_keywords": [
            "john",
            "target username",
            "198.51.100.23"
        ],
        "relevance_keywords": [
            "account",
            "username",
            "john",
            "targeted"
        ]
    },
    {
        "question": (
            "Explain network event NET001 and its details."
        ),
        "expected_facts": [
            "NET001",
            "198.51.100.23",
            "192.0.2.100",
            "TCP",
            "443",
            "high"
        ],
        "retrieval_keywords": [
            "NET001",
            "198.51.100.23",
            "192.0.2.100",
            "suspicious_connection"
        ],
        "relevance_keywords": [
            "NET001",
            "timestamp",
            "source IP",
            "destination IP",
            "protocol",
            "port"
        ]
    }
]


# -----------------------------------------
# ANSWER FACT COVERAGE
# -----------------------------------------

def calculate_answer_accuracy(answer, expected_facts):

    answer_lower = answer.lower()

    matched_facts = [
        fact
        for fact in expected_facts
        if fact.lower() in answer_lower
    ]

    accuracy = (
        len(matched_facts) / len(expected_facts)
    ) * 100

    return accuracy, matched_facts


# -----------------------------------------
# RETRIEVAL KEYWORD COVERAGE
# -----------------------------------------

def calculate_retrieval_coverage(
    retrieved_documents,
    retrieval_keywords
):

    retrieved_text = " ".join(
        document.page_content
        for document in retrieved_documents
    ).lower()

    matched_keywords = [
        keyword
        for keyword in retrieval_keywords
        if keyword.lower() in retrieved_text
    ]

    coverage = (
        len(matched_keywords) / len(retrieval_keywords)
    ) * 100

    return coverage, matched_keywords


# -----------------------------------------
# SOURCE DIVERSITY
# -----------------------------------------

def calculate_source_diversity(retrieved_documents):

    sources = set(
        document.metadata.get("source", "Unknown")
        for document in retrieved_documents
    )

    return len(sources)


# -----------------------------------------
# ANSWER RELEVANCE
# -----------------------------------------

def calculate_answer_relevance(
    answer,
    relevance_keywords
):

    answer_lower = answer.lower()

    matched_keywords = [
        keyword
        for keyword in relevance_keywords
        if keyword.lower() in answer_lower
    ]

    relevance = (
        len(matched_keywords) / len(relevance_keywords)
    ) * 100

    return relevance, matched_keywords


# -----------------------------------------
# FAITHFULNESS CHECK
# -----------------------------------------

def calculate_faithfulness(
    answer,
    retrieved_documents,
    expected_facts
):

    context = " ".join(
        document.page_content
        for document in retrieved_documents
    ).lower()

    answer_lower = answer.lower()

    # Check which expected facts appear in both
    # the generated answer and retrieved context.

    answer_facts = [
        fact
        for fact in expected_facts
        if fact.lower() in answer_lower
    ]

    supported_facts = [
        fact
        for fact in answer_facts
        if fact.lower() in context
    ]

    if not answer_facts:

        return 0.0, [], []

    faithfulness = (
        len(supported_facts) / len(answer_facts)
    ) * 100

    unsupported_facts = [
        fact
        for fact in answer_facts
        if fact.lower() not in context
    ]

    return (
        faithfulness,
        supported_facts,
        unsupported_facts
    )


# -----------------------------------------
# AVERAGE CALCULATION
# -----------------------------------------

def calculate_average(values):

    if not values:
        return 0.0

    return sum(values) / len(values)


# -----------------------------------------
# MAIN EVALUATION PIPELINE
# -----------------------------------------

def main():

    print("\n========== CYBERSHIELD AI ==========")
    print("          RAG EVALUATION")
    print("====================================")

    # Step 1: Rebuild vector database

    print("\nRebuilding vector database...")

    vector_store, chunks = create_vector_store()

    print("\nChunks created:", len(chunks))

    stored_count = vector_store._collection.count()

    print("Vectors stored:", stored_count)

    if stored_count != len(chunks):

        raise ValueError(
            "Vector count does not match chunk count."
        )

    print("\nVector database verification successful!")

    # Step 2: Create BM25 retriever

    bm25_retriever = BM25Retriever.from_documents(
        chunks,
        k=5
    )

    # Step 3: Load reranker

    reranker = load_reranker()

    # Metric storage

    all_accuracy = []
    all_coverage = []
    all_relevance = []
    all_faithfulness = []

    all_retrieval_latency = []
    all_answer_latency = []

    # -------------------------------------
    # RUN TEST CASES
    # -------------------------------------

    for index, test_case in enumerate(
        TEST_CASES,
        start=1
    ):

        question = test_case["question"]

        expected_facts = test_case["expected_facts"]

        retrieval_keywords = test_case["retrieval_keywords"]

        relevance_keywords = test_case["relevance_keywords"]

        print("\n====================================")
        print(f"          TEST CASE {index}")
        print("====================================")

        print("\nQuestion:")
        print(question)

        # Step 4: Retrieval and reranking

        retrieval_start = time.perf_counter()

        hybrid_results = hybrid_search(
            question,
            vector_store,
            bm25_retriever
        )

        reranked_results = rerank_documents(
            question,
            hybrid_results,
            reranker
        )

        retrieved_documents = [
            document
            for document, score in reranked_results[:5]
        ]

        retrieval_latency = (
            time.perf_counter() - retrieval_start
        )

        print("\nRetrieved Documents:", len(retrieved_documents))

        # Step 5: Retrieval coverage

        retrieval_coverage, matched_keywords = (
            calculate_retrieval_coverage(
                retrieved_documents,
                retrieval_keywords
            )
        )

        # Step 6: Answer generation

        answer_start = time.perf_counter()

        answer = generate_answer(
            question,
            retrieved_documents
        )

        answer_latency = (
            time.perf_counter() - answer_start
        )

        # Step 7: Answer fact coverage

        answer_accuracy, matched_facts = (
            calculate_answer_accuracy(
                answer,
                expected_facts
            )
        )

        # Step 8: Answer relevance

        relevance, relevance_matches = (
            calculate_answer_relevance(
                answer,
                relevance_keywords
            )
        )

        # Step 9: Faithfulness

        (
            faithfulness,
            supported_facts,
            unsupported_facts
        ) = calculate_faithfulness(
            answer,
            retrieved_documents,
            expected_facts
        )

        # Step 10: Source diversity

        source_count = calculate_source_diversity(
            retrieved_documents
        )

        # Store metrics

        all_accuracy.append(answer_accuracy)
        all_coverage.append(retrieval_coverage)
        all_relevance.append(relevance)
        all_faithfulness.append(faithfulness)

        all_retrieval_latency.append(retrieval_latency)
        all_answer_latency.append(answer_latency)

        # ---------------------------------
        # DISPLAY RESULTS
        # ---------------------------------

        print("\nGenerated Answer:")
        print(answer)

        print("\n---------- EVALUATION RESULTS ----------")

        print(
            f"Answer Fact Coverage: {answer_accuracy:.2f}%"
        )

        print(
            f"Retrieval Keyword Coverage: "
            f"{retrieval_coverage:.2f}%"
        )

        print(
            f"Answer Relevance Indicator: "
            f"{relevance:.2f}%"
        )

        print(
            f"Faithfulness Fact Support Indicator: "
            f"{faithfulness:.2f}%"
        )

        print("\nMatched Expected Facts:", matched_facts)

        print("Matched Retrieval Keywords:", matched_keywords)

        print("Relevance Keyword Matches:", relevance_matches)

        print("Supported Expected Facts:", supported_facts)

        print("Unsupported Expected Facts:", unsupported_facts)

        print("Unique Sources Retrieved:", source_count)

        print(
            f"Retrieval + Reranking Latency: "
            f"{retrieval_latency:.2f} seconds"
        )

        print(
            f"Answer Generation Latency: "
            f"{answer_latency:.2f} seconds"
        )

        print("----------------------------------------")

    # -------------------------------------
    # FINAL SUMMARY
    # -------------------------------------

    print("\n========== FINAL EVALUATION ==========")

    print(
        f"Average Answer Fact Coverage: "
        f"{calculate_average(all_accuracy):.2f}%"
    )

    print(
        f"Average Retrieval Keyword Coverage: "
        f"{calculate_average(all_coverage):.2f}%"
    )

    print(
        f"Average Answer Relevance Indicator: "
        f"{calculate_average(all_relevance):.2f}%"
    )

    print(
        f"Average Faithfulness Fact Support Indicator: "
        f"{calculate_average(all_faithfulness):.2f}%"
    )

    print("\n========== LATENCY SUMMARY ==========")

    print(
        f"Average Retrieval + Reranking: "
        f"{calculate_average(all_retrieval_latency):.2f} seconds"
    )

    print(
        f"Average Answer Generation: "
        f"{calculate_average(all_answer_latency):.2f} seconds"
    )

    print("\nTotal Test Cases:", len(TEST_CASES))

    print("\nRAG evaluation completed!")

    print("\nNote:")
    print(
        "Relevance and faithfulness are rule-based indicators, "
        "not formal semantic evaluation scores."
    )


if __name__ == "__main__":
    main()
