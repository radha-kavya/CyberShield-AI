
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from rag.llm import get_llm
from retrieval.reranker import load_reranker, rerank_documents


def extract_field(pattern, text, default=None):
    """Extract one field from document text."""

    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)

    if match:
        return match.group(1).strip()

    return default


def extract_evidence(retrieved_documents):
    """
    Extract structured incident and network evidence.

    Prefer network events that match the incident source IP.
    Avoid mixing unrelated network events.
    """

    combined_text = "\n".join(
        document.page_content
        for document in retrieved_documents
    )

    # 1. Extract all IP addresses
    ip_addresses = list(dict.fromkeys(
        re.findall(
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            combined_text
        )
    ))

    # 2. Identify the incident source IP
    incident_source_ips = []

    for document in retrieved_documents:
        source_ip = extract_field(
            r"^\s*(?:Source IP|source_ip)\s*:\s*"
            r"((?:\d{1,3}\.){3}\d{1,3})",
            document.page_content
        )

        if source_ip:
            incident_source_ips.append(source_ip)

    incident_source_ips = list(dict.fromkeys(incident_source_ips))

    # 3. Extract targeted usernames
    username_patterns = [
        r"(?im)^\s*Target username\s*:\s*['\"`]?([a-zA-Z0-9_.-]+)",
        r"(?i)targeted username\s*(?:is|:)\s*['\"`]?([a-zA-Z0-9_.-]+)",
        r"(?i)targeted account\s*(?:is|:)\s*['\"`]?([a-zA-Z0-9_.-]+)"
    ]

    usernames = []

    for pattern in username_patterns:
        usernames.extend(
            re.findall(pattern, combined_text)
        )

    usernames = list(dict.fromkeys(usernames))

    # 4. Extract failed-login count
    failed_attempt_count = None

    failed_patterns = [
        r"(?i)\b(three|3)\s+failed login attempts?",
        r"(?i)\b(\d+)\s+failed login attempts?"
    ]

    for pattern in failed_patterns:
        match = re.search(pattern, combined_text)

        if match:
            value = match.group(1).lower()

            failed_attempt_count = (
                3 if value == "three"
                else int(value)
            )
            break

    # 5. Find explicitly related network event IDs
    related_event_ids = re.findall(
        r"(?i)\brelated\s+(?:network\s+)?event"
        r"(?:\s+ID)?\s*[:#]?\s*(NET\d+)\b",
        combined_text
    )

    related_event_ids = list(dict.fromkeys(
        event_id.upper()
        for event_id in related_event_ids
    ))

    # 6. Extract structured network event records
    network_events = []

    for document in retrieved_documents:
        content = document.page_content

        event_id = extract_field(
            r"^\s*event_id\s*:\s*(NET\d+)",
            content
        )

        if not event_id:
            continue

        event = {
            "Event ID": event_id.upper(),
            "Timestamp": extract_field(
                r"^\s*timestamp\s*:\s*(.+)$",
                content
            ),
            "Source IP": extract_field(
                r"^\s*source_ip\s*:\s*(.+)$",
                content
            ),
            "Destination IP": extract_field(
                r"^\s*destination_ip\s*:\s*(.+)$",
                content
            ),
            "Event Type": extract_field(
                r"^\s*event_type\s*:\s*(.+)$",
                content
            ),
            "Protocol": extract_field(
                r"^\s*protocol\s*:\s*(.+)$",
                content
            ),
            "Port": extract_field(
                r"^\s*port\s*:\s*(.+)$",
                content
            ),
            "Severity": extract_field(
                r"^\s*severity\s*:\s*(.+)$",
                content
            ),
            "Description": extract_field(
                r"^\s*description\s*:\s*(.+)$",
                content
            ),
            "Source File": document.metadata.get(
                "source", "Unknown source"
            )
        }

        network_events.append(event)

    # 7. Select only relevant network events
    if related_event_ids:
        selected_events = [
            event for event in network_events
            if event["Event ID"] in related_event_ids
        ]
    elif incident_source_ips:
        selected_events = [
            event for event in network_events
            if event["Source IP"] in incident_source_ips
        ]
    else:
        selected_events = network_events

    # 8. Extract incident timestamps separately
    timestamps = list(dict.fromkeys(
        re.findall(
            r"\b\d{2}:\d{2}:\d{2}\b",
            combined_text
        )
    ))

    # 9. Extract source filenames
    sources = list(dict.fromkeys(
        document.metadata.get("source", "Unknown source")
        for document in retrieved_documents
    ))

    return {
        "IP Addresses": ip_addresses,
        "Incident Source IPs": incident_source_ips,
        "Targeted Usernames": usernames,
        "Failed Login Attempts": failed_attempt_count,
        "Related Event IDs": [
            event["Event ID"] for event in selected_events
        ],
        "Network Event Details": selected_events,
        "Timestamps": timestamps,
        "Source Files": sources
    }


def generate_answer(question, retrieved_documents):

    evidence = extract_evidence(retrieved_documents)

    # Give each retrieved document a source label.
    context_parts = []
    source_map = []

    for index, document in enumerate(
        retrieved_documents, start=1
    ):

        source_label = f"S{index}"

        source = document.metadata.get(
            "source", "Unknown source"
        )

        context_parts.append(
            f"""
[{source_label}]
Source file: {source}

Content:
{document.page_content}
"""
        )

        source_map.append(
            f"[{source_label}] {source}"
        )

    context = "\n".join(context_parts)

    evidence_text = "\n".join(
        f"{key}: {value if value else 'Not found'}"
        for key, value in evidence.items()
    )

    prompt = ChatPromptTemplate.from_template(
        """
You are CyberShield AI, a defensive cybersecurity
investigation assistant.

Answer the user's question using ONLY the supplied
retrieved documents and extracted evidence.

IMPORTANT RULES:

1. Never invent IP addresses, usernames, event IDs,
   timestamps, ports, protocols or severity values.

2. Use only network events included in
   "Network Event Details".

3. Do not introduce unrelated event IDs from other
   retrieved documents.

4. If NET001 is the related event, do not replace it
   with another event.

5. Keep login activity and network activity separate.

6. Do not describe a network event timestamp as a
   login-attempt timestamp.

7. Include destination IP, protocol, port and severity
   when these fields are available in the evidence.

8. If a field is unavailable, say "Not available".

9. Cite factual findings next to the statements using
   the source labels, such as [S1] and [S2].

10. Do not cite a source unless it supports the claim.

11. Separate observed facts from possible explanations.

12. Suspicious activity does not prove a successful
    cyberattack.

13. Never claim an IP address is malicious unless
    the supplied evidence establishes that fact.

14. Use simple language suitable for a security analyst.

15. Answer the specific user question. Do not add
    unrelated events or unnecessary timelines.

For a complete investigation question, use these sections:

1. SUSPICIOUS IP
2. OBSERVED LOGIN ACTIVITY
3. TARGETED ACCOUNT
4. RELATED NETWORK EVENTS
5. TIMELINE
6. WHY IT IS SUSPICIOUS
7. DEFENSIVE INVESTIGATION STEPS
8. SOURCE FILES

Extracted Evidence:
{evidence}

Retrieved Context:
{context}

User Question:
{question}

Answer:
"""
    )

    llm = get_llm()

    rag_chain = prompt | llm | StrOutputParser()

    response = rag_chain.invoke({
        "evidence": evidence_text,
        "context": context,
        "question": question
    })

    source_list = "\n".join(source_map)

    return (
        f"{response}\n\n"
        f"SOURCE LABELS:\n{source_list}"
    )


def main():

    print("\n========== CYBERSHIELD AI ==========")
    print("       COMPLETE RAG PIPELINE")
    print("====================================")

    from ingestion.ingest_all import ingest_all_documents
    from processing.chunker import split_documents
    from processing.embeddings import create_embedding_model

    from langchain_chroma import Chroma
    from langchain_community.retrievers import BM25Retriever

    from retrieval.hybrid_search import hybrid_search

    # Step 1: Load and chunk documents
    print("\nLoading cybersecurity documents...")

    documents = ingest_all_documents()

    chunks = split_documents(documents)

    print("\nDocuments:", len(documents))
    print("Chunks:", len(chunks))

    # Step 2: Connect to ChromaDB
    embedding_model = create_embedding_model()

    vector_store = Chroma(
        collection_name="cybershield_documents",
        embedding_function=embedding_model,
        persist_directory="vector_db/cybershield_chroma"
    )

    print(
        "\nStored Vectors:",
        vector_store._collection.count()
    )

    # Step 3: Create BM25 retriever
    bm25_retriever = BM25Retriever.from_documents(
        chunks,
        k=5
    )

    # Step 4: User question
    question = (
        "Why is IP 198.51.100.23 suspicious? "
        "Identify the targeted username and related events."
    )

    print("\nUser Question:")
    print(question)

    # Step 5: Hybrid search
    print("\nPerforming hybrid search...")

    hybrid_results = hybrid_search(
        question,
        vector_store,
        bm25_retriever
    )

    print("\nHybrid Results:", len(hybrid_results))

    # Step 6: Cross-Encoder reranking
    reranker = load_reranker()

    reranked_results = rerank_documents(
        question,
        hybrid_results,
        reranker
    )

    print("\nReranked Results:", len(reranked_results))

    # Step 7: Select top 5 documents
    ranked_documents = [
        document
        for document, score in reranked_results[:5]
    ]

    # Step 8: Extract evidence
    print("\n========== EXTRACTED EVIDENCE ==========")

    evidence = extract_evidence(ranked_documents)

    for key, value in evidence.items():
        print(f"{key}: {value if value else 'Not found'}")

    # Step 9: Generate answer
    print("\nGenerating investigation report using Qwen...")

    answer = generate_answer(
        question,
        ranked_documents
    )

    # Step 10: Display report
    print("\n========== INVESTIGATION REPORT ==========")
    print(answer)

    # Step 11: Display retrieval ranking
    print("\n========== RETRIEVED SOURCES ==========")

    for index, (document, score) in enumerate(
        reranked_results[:5],
        start=1
    ):

        print(f"\nRank: {index}")

        print(
            "Source:",
            document.metadata.get("source")
        )

        print(
            "Cross-Encoder Score:",
            round(score, 4)
        )

    print("\nComplete RAG pipeline executed successfully!")


if __name__ == "__main__":
    main()
