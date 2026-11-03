
import requests
from bs4 import BeautifulSoup

from langchain_core.documents import Document


def load_web_documents(url):

    headers = {
        "User-Agent": "CyberShieldAI/1.0 (educational project)"
    }

    # 1. Fetch webpage
    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    # 2. Parse HTML
    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # 3. Extract page title
    page_title = (
        soup.title.get_text(strip=True)
        if soup.title else "Cybersecurity Webpage"
    )

    # 4. Remove unnecessary elements
    for element in soup([
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "noscript"
    ]):
        element.decompose()

    # 5. Extract readable content
    content = soup.get_text(
        separator="\n",
        strip=True
    )

    # 6. Validate content
    if len(content) < 100:
        raise ValueError(
            "Unable to extract sufficient webpage content."
        )

    # 7. Create LangChain Document
    document = Document(
        page_content=content,
        metadata={
            "source": url,
            "title": page_title,
            "document_type": "web_threat_intelligence",
            "file_type": "web"
        }
    )

    return [document]


if __name__ == "__main__":

    # OWASP Top 10 cybersecurity resource
    url = "https://owasp.org/www-project-top-ten/"

    try:

        documents = load_web_documents(url)

        print("\n========== CYBERSHIELD AI ==========")
        print("             WEB PAGE LOADER")
        print("====================================")

        print(f"\nTotal documents loaded: {len(documents)}")

        for document in documents:

            print("\n------------------------------------")
            print("Source:", document.metadata["source"])
            print("Title:", document.metadata["title"])
            print("Document Type:", document.metadata["document_type"])

            print("\nDocument Content:")
            print(document.page_content[:3000])

        print("\n====================================")
        print("Web page loading completed successfully!")

    except requests.RequestException as error:

        print("\nUnable to load webpage:", error)

    except ValueError as error:

        print("\nContent extraction error:", error)
