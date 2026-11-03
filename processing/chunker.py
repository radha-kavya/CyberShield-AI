
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ingestion.ingest_all import ingest_all_documents


# Chunking configuration by document type
CHUNK_CONFIG = {
    "login_logs": {
        "chunk_size": 500,
        "chunk_overlap": 50
    },
    "network_events": {
        "chunk_size": 500,
        "chunk_overlap": 50
    },
    "incident_report": {
        "chunk_size": 700,
        "chunk_overlap": 100
    },
    "security_policy": {
        "chunk_size": 800,
        "chunk_overlap": 100
    },
    "threat_intelligence": {
        "chunk_size": 800,
        "chunk_overlap": 100
    },
    "default": {
        "chunk_size": 700,
        "chunk_overlap": 100
    }
}


def get_chunk_config(document):

    document_type = document.metadata.get(
        "document_type", ""
    ).lower()

    source = document.metadata.get(
        "source", ""
    ).lower()

    # Identify document category
    if "login_logs" in source:
        config_key = "login_logs"

    elif "network_events" in source:
        config_key = "network_events"

    elif document_type in CHUNK_CONFIG:
        config_key = document_type

    elif document_type == "html":
        config_key = "threat_intelligence"

    else:
        config_key = "default"

    return CHUNK_CONFIG[config_key]


def split_documents(documents):

    all_chunks = []

    for document in documents:

        # Skip empty documents
        if not document.page_content.strip():
            continue

        # Get document-specific configuration
        config = get_chunk_config(document)

        # Create splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"],
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

        # Split individual document
        document_chunks = text_splitter.split_documents(
            [document]
        )

        all_chunks.extend(document_chunks)

    return all_chunks


if __name__ == "__main__":

    # 1. Load original documents
    documents = ingest_all_documents()

    # 2. Apply advanced chunking
    chunks = split_documents(documents)

    print("\n========== CYBERSHIELD AI ==========")
    print("       ADVANCED DOCUMENT CHUNKING")
    print("====================================")

    print("\nOriginal Documents:", len(documents))
    print("Total Chunks:", len(chunks))

    print("\nChunking Configuration:")

    for document_type, config in CHUNK_CONFIG.items():

        print(
            f"{document_type}: "
            f"Size={config['chunk_size']}, "
            f"Overlap={config['chunk_overlap']}"
        )

    print("\n------------------------------------")
    print("SAMPLE CHUNKS")
    print("------------------------------------")

    for index, chunk in enumerate(chunks[:5], start=1):

        print(f"\nChunk {index}")

        print("Content:")
        print(chunk.page_content[:500])

        print("\nContent Length:", len(chunk.page_content))

        print("\nMetadata:")
        print(chunk.metadata)

        print("------------------------------------")

    print("\n====================================")
    print("Advanced document chunking completed successfully!")
