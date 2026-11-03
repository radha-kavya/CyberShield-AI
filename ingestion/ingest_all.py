
from ingestion.csv_loader import load_csv_documents
from ingestion.json_loader import load_json_documents
from ingestion.pdf_loader import load_pdf_documents
from ingestion.docx_loader import load_docx_documents
from ingestion.markdown_loader import load_markdown_documents
from ingestion.excel_loader import load_excel_documents
from ingestion.html_loader import load_html_documents
from ingestion.web_loader import load_web_documents


def ingest_all_documents():

    all_documents = []

    print("\n========== CYBERSHIELD AI ==========")
    print("       CENTRAL INGESTION PIPELINE")
    print("====================================")

    # 1. CSV Documents
    csv_docs = load_csv_documents(
        "data/logs/login_logs.csv"
    )
    all_documents.extend(csv_docs)
    print(f"CSV Documents       : {len(csv_docs)}")

    # 2. JSON Documents
    json_docs = load_json_documents(
        "data/logs/network_events.json"
    )
    all_documents.extend(json_docs)
    print(f"JSON Documents      : {len(json_docs)}")

    # 3. PDF Documents
    pdf_docs = load_pdf_documents(
        "data/policies/security_policy.pdf"
    )
    all_documents.extend(pdf_docs)
    print(f"PDF Documents       : {len(pdf_docs)}")

    # 4. DOCX Documents
    docx_docs = load_docx_documents(
        "data/incidents/incident_report.docx"
    )
    all_documents.extend(docx_docs)
    print(f"DOCX Documents      : {len(docx_docs)}")

    # 5. Markdown Documents
    markdown_docs = load_markdown_documents(
        "data/threat_intelligence/ssh_threat_report.md"
    )
    all_documents.extend(markdown_docs)
    print(f"Markdown Documents  : {len(markdown_docs)}")

    # 6. Excel Documents
    excel_docs = load_excel_documents(
        "data/logs/security_events.xlsx"
    )
    all_documents.extend(excel_docs)
    print(f"Excel Documents     : {len(excel_docs)}")

    # 7. HTML Documents
    html_docs = load_html_documents(
        "data/threat_intelligence/security_advisory.html"
    )
    all_documents.extend(html_docs)
    print(f"HTML Documents      : {len(html_docs)}")

    # 8. Web Documents
    web_docs = load_web_documents(
        "https://owasp.org/www-project-top-ten/"
    )
    all_documents.extend(web_docs)
    print(f"Web Documents       : {len(web_docs)}")

    # Final count
    print("\n------------------------------------")
    print(f"TOTAL DOCUMENTS     : {len(all_documents)}")
    print("------------------------------------")

    return all_documents


if __name__ == "__main__":

    documents = ingest_all_documents()

    print("\nIngestion pipeline completed successfully!")

    print("\nSample document:")
    print("Content:", documents[0].page_content[:300])
    print("Metadata:", documents[0].metadata)
