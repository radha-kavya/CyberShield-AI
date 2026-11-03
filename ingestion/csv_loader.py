import pandas as pd
from pathlib import Path

from langchain_core.documents import Document


def load_csv_documents(file_path):

    # Read CSV file
    df = pd.read_csv(file_path)

    documents = []

    # Convert each row into a LangChain Document
    for _, row in df.iterrows():

        content = "\n".join(
            f"{key}: {value}"
            for key, value in row.items()
        )

        document = Document(
            page_content=content,
            metadata={
                "source": str(file_path),
                "username": str(row["username"]),
                "source_ip": str(row["source_ip"]),
                "status": str(row["status"]),
                "severity": str(row["severity"])
            }
        )

        documents.append(document)

    return documents


if __name__ == "__main__":

    file_path = Path("data/logs/login_logs.csv")

    documents = load_csv_documents(file_path)

    print("\n========== CYBERSHIELD AI ==========")
    print("          CSV DOCUMENT LOADER")
    print("====================================")

    print(f"\nTotal documents loaded: {len(documents)}")

    for document in documents:

        print("\n------------------------------------")
        print("Username :", document.metadata["username"])
        print("Source IP:", document.metadata["source_ip"])
        print("Status   :", document.metadata["status"])
        print("Severity :", document.metadata["severity"])

        print("\nDocument Content:")
        print(document.page_content)

    print("\n====================================")
    print("CSV loading completed successfully!")