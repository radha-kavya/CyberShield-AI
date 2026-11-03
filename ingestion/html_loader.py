from pathlib import Path
from bs4 import BeautifulSoup

from langchain_core.documents import Document


def load_html_documents(file_path):

    # Read HTML file
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Extract readable text from HTML
    soup = BeautifulSoup(html_content, "html.parser")

    content = soup.get_text(separator="\n", strip=True)

    # Convert into LangChain Document
    document = Document(
        page_content=content,
        metadata={
            "source": str(file_path),
            "document_type": "security_advisory",
            "file_type": "html"
        }
    )

    return [document]


if __name__ == "__main__":

    file_path = Path(
        "data/threat_intelligence/security_advisory.html"
    )

    documents = load_html_documents(file_path)

    print("\n========== CYBERSHIELD AI ==========")
    print("           HTML DOCUMENT LOADER")
    print("====================================")

    print(f"\nTotal documents loaded: {len(documents)}")

    for document in documents:

        print("\n------------------------------------")
        print("Source:", document.metadata["source"])
        print("Document Type:", document.metadata["document_type"])

        print("\nDocument Content:")
        print(document.page_content)

    print("\n====================================")
    print("HTML loading completed successfully!")