
import json
from pathlib import Path

from langchain_core.documents import Document


def load_json_documents(file_path):

    # Read JSON file
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    documents = []

    # Convert each JSON event into a LangChain Document
    for event in data:

        content = "\n".join(
            f"{key}: {value}"
            for key, value in event.items()
        )

        document = Document(
            page_content=content,
            metadata={
                "source": str(file_path),
                "event_id": event.get("event_id", "unknown"),
                "severity": event.get("severity", "unknown"),
                "event_type": event.get("event_type", "unknown"),
                "source_ip": event.get("source_ip", "unknown")
            }
        )

        documents.append(document)

    return documents


if __name__ == "__main__":

    file_path = Path("data/logs/network_events.json")

    documents = load_json_documents(file_path)

    print("\n========== CYBERSHIELD AI ==========")
    print("          JSON DOCUMENT LOADER")
    print("====================================")

    print(f"\nTotal documents loaded: {len(documents)}")

    for document in documents:

        print("\n------------------------------------")
        print("Event ID :", document.metadata["event_id"])
        print("Severity :", document.metadata["severity"])
        print("Source IP:", document.metadata["source_ip"])
        print("\nDocument Content:")
        print(document.page_content)

    print("\n====================================")
    print("JSON loading completed successfully!")
