
from langchain_huggingface import HuggingFaceEmbeddings

from processing.chunker import split_documents
from ingestion.ingest_all import ingest_all_documents


def create_embedding_model():

    print("\nLoading HuggingFace embedding model...")

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        }
    )

    return embedding_model


if __name__ == "__main__":

    # 1. Load documents
    documents = ingest_all_documents()

    # 2. Create chunks
    chunks = split_documents(documents)

    # 3. Load embedding model
    embedding_model = create_embedding_model()

    # 4. Convert sample text into vector
    sample_text = chunks[0].page_content

    vector = embedding_model.embed_query(sample_text)

    # 5. Display results
    print("\n========== CYBERSHIELD AI ==========")
    print("          HUGGINGFACE EMBEDDINGS")
    print("====================================")

    print("\nEmbedding Model:")
    print("sentence-transformers/all-MiniLM-L6-v2")

    print("\nTotal Chunks:", len(chunks))

    print("\nSample Text:")
    print(sample_text)

    print("\nEmbedding Vector:")
    print(vector[:10])

    print("\nVector Dimensions:")
    print(len(vector))

    print("\n====================================")
    print("Embedding generation completed successfully!")
