from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever

from ingestion.ingest_all import ingest_all_documents
from processing.chunker import split_documents
from processing.embeddings import create_embedding_model

from retrieval.hybrid_search import hybrid_search
from retrieval.reranker import load_reranker, rerank_documents

from rag.conversational_rag import (
    contextualize_question,
    update_chat_history
)

from rag.answer_generator import generate_answer


def create_retrievers():

    print("\nLoading CyberShield AI documents...")

    documents = ingest_all_documents()
    chunks = split_documents(documents)

    print("\nTotal Documents:", len(documents))
    print("Total Chunks:", len(chunks))

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

    return vector_store, bm25_retriever


def conversational_search(
    question,
    chat_history,
    vector_store,
    bm25_retriever,
    reranker
):

    # Step 1: Transform follow-up question
    contextual_question = contextualize_question(
        question,
        chat_history
    )

    print("\nOriginal Question:")
    print(question)

    print("\nContextualized Question:")
    print(contextual_question)

    # Step 2: Hybrid retrieval
    print("\nPerforming hybrid search...")

    hybrid_results = hybrid_search(
        contextual_question,
        vector_store,
        bm25_retriever
    )

    print("Hybrid Results:", len(hybrid_results))

    # Step 3: Cross-Encoder reranking
    print("\nPerforming reranking...")

    reranked_results = rerank_documents(
        contextual_question,
        hybrid_results,
        reranker
    )

    print("Reranked Results:", len(reranked_results))

    # Step 4: Select top 5 documents
    ranked_documents = [
        document
        for document, score in reranked_results[:5]
    ]

    # Step 5: Generate answer using Qwen
    print("\nGenerating answer using Qwen...")

    answer = generate_answer(
        contextual_question,
        ranked_documents
    )

    # Step 6: Display retrieved sources
    print("\n========== RETRIEVED SOURCES ==========")

    for index, (document, score) in enumerate(
        reranked_results[:5],
        start=1
    ):

        print(f"\nRank: {index}")
        print("Source:", document.metadata.get("source"))
        print("Reranker Score:", round(score, 4))

    return answer, len(reranked_results)


def main():

    print("\n========== CYBERSHIELD AI ==========")
    print("       CONVERSATIONAL RAG")
    print("====================================")

    # Step 1: Create retrievers
    vector_store, bm25_retriever = create_retrievers()

    # Step 2: Load reranker
    print("\nLoading Cross-Encoder model...")

    reranker = load_reranker()

    # Step 3: Initialize conversation history
    chat_history = []

    # ==================================
    # QUESTION 1
    # ==================================

    question1 = "Why is IP 198.51.100.23 suspicious?"

    print("\n========== QUESTION 1 ==========")

    answer1, count1 = conversational_search(
        question1,
        chat_history,
        vector_store,
        bm25_retriever,
        reranker
    )

    print("\n========== ANSWER 1 ==========")
    print(answer1)

    # Save first conversation
    chat_history = update_chat_history(
        chat_history,
        question1,
        answer1
    )

    # ==================================
    # QUESTION 2 - FOLLOW-UP
    # ==================================

    question2 = "Which account did it target?"

    print("\n========== QUESTION 2 ==========")

    answer2, count2 = conversational_search(
        question2,
        chat_history,
        vector_store,
        bm25_retriever,
        reranker
    )

    print("\n========== ANSWER 2 ==========")
    print(answer2)

    # Save follow-up conversation
    chat_history = update_chat_history(
        chat_history,
        question2,
        answer2
    )

    # ==================================
    # QUESTION 3 - FOLLOW-UP
    # ==================================

    question3 = "What was the related network event?"

    print("\n========== QUESTION 3 ==========")

    answer3, count3 = conversational_search(
        question3,
        chat_history,
        vector_store,
        bm25_retriever,
        reranker
    )

    print("\n========== ANSWER 3 ==========")
    print(answer3)

    # Save third conversation
    chat_history = update_chat_history(
        chat_history,
        question3,
        answer3
    )

    # ==================================
    # CONVERSATION SUMMARY
    # ==================================

    print("\n========== CONVERSATION SUMMARY ==========")

    print("Question 1 Retrieved Documents:", count1)
    print("Question 2 Retrieved Documents:", count2)
    print("Question 3 Retrieved Documents:", count3)

    print("Total Conversation Messages:", len(chat_history))

    print("\n========== CHAT HISTORY ==========")

    for message in chat_history:

        print(f"\n{message['role'].upper()}:")
        print(message["content"][:500])

        print("------------------------------------")

    print("\nConversational RAG pipeline completed successfully!")


if __name__ == "__main__":
    main()