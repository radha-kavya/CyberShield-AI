from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


def load_pdf_documents(file_path):

    # Load PDF document
    loader = PyPDFLoader(str(file_path))

    documents = loader.load()

    # Add metadata
    for document in documents:

        document.metadata["source"] = str(file_path)
        document.metadata["document_type"] = "security_policy"

    return documents


if __name__ == "__main__":

    file_path = Path("data/policies/security_policy.pdf")

    documents = load_pdf_documents(file_path)

    print("\n========== CYBERSHIELD AI ==========")
    print("          PDF DOCUMENT LOADER")
    print("====================================")

    print(f"\nTotal pages loaded: {len(documents)}")

    for document in documents:

        print("\n------------------------------------")
        print("Page Number:", document.metadata.get("page", "Unknown"))
        print("Source:", document.metadata["source"])

        print("\nDocument Content:")
        print(document.page_content)

    print("\n====================================")
    print("PDF loading completed successfully!")