from pathlib import Path

from langchain_community.document_loaders import Docx2txtLoader


def load_docx_documents(file_path):

    # Load Word document
    loader = Docx2txtLoader(str(file_path))

    documents = loader.load()

    # Add metadata
    for document in documents:

        document.metadata["source"] = str(file_path)
        document.metadata["document_type"] = "incident_report"

    return documents


if __name__ == "__main__":

    file_path = Path("data/incidents/incident_report.docx")

    documents = load_docx_documents(file_path)

    print("\n========== CYBERSHIELD AI ==========")
    print("          DOCX DOCUMENT LOADER")
    print("====================================")

    print(f"\nTotal documents loaded: {len(documents)}")

    for document in documents:

        print("\n------------------------------------")
        print("Source:", document.metadata["source"])
        print("Document Type:", document.metadata["document_type"])

        print("\nDocument Content:")
        print(document.page_content)

    print("\n====================================")
    print("DOCX loading completed successfully!")