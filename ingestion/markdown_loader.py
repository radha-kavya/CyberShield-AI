from pathlib import Path

from langchain_core.documents import Document


def load_markdown_documents(file_path):

    # Read Markdown file
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Convert content into LangChain Document
    document = Document(
        page_content=content,
        metadata={
            "source": str(file_path),
            "document_type": "threat_intelligence",
            "file_type": "markdown"
        }
    )

    return [document]


if __name__ == "__main__":

    file_path = Path(
        "data/threat_intelligence/ssh_threat_report.md"
    )

    documents = load_markdown_documents(file_path)

    print("\n========== CYBERSHIELD AI ==========")
    print("        MARKDOWN DOCUMENT LOADER")
    print("====================================")

    print(f"\nTotal documents loaded: {len(documents)}")

    for document in documents:

        print("\n------------------------------------")
        print("Source:", document.metadata["source"])
        print("Document Type:", document.metadata["document_type"])

        print("\nDocument Content:")
        print(document.page_content)

    print("\n====================================")
    print("Markdown loading completed successfully!")