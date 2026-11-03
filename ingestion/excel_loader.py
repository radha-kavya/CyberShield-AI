import pandas as pd
from pathlib import Path

from langchain_core.documents import Document


def load_excel_documents(file_path):

    # Read Excel file
    df = pd.read_excel(file_path)

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
                "event_id": str(row["event_id"]),
                "source_ip": str(row["source_ip"]),
                "severity": str(row["severity"]),
                "file_type": "excel"
            }
        )

        documents.append(document)

    return documents


if __name__ == "__main__":

    file_path = Path("data/logs/security_events.xlsx")

    documents = load_excel_documents(file_path)

    print("\n========== CYBERSHIELD AI ==========")
    print("          EXCEL DOCUMENT LOADER")
    print("====================================")

    print(f"\nTotal documents loaded: {len(documents)}")

    for document in documents:

        print("\n------------------------------------")
        print("Event ID :", document.metadata["event_id"])
        print("Source IP:", document.metadata["source_ip"])
        print("Severity :", document.metadata["severity"])

        print("\nDocument Content:")
        print(document.page_content)

    print("\n====================================")
    print("Excel loading completed successfully!")