
import re


def transform_query(query):

    """
    Expand cybersecurity questions with relevant search terms.
    Preserve the original question and important identifiers.
    """

    original_query = query.strip()

    if not original_query:
        raise ValueError("Query cannot be empty.")

    query_lower = original_query.lower()

    transformed_terms = []

    # 1. Detect IP addresses
    ip_addresses = re.findall(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        original_query
    )

    if ip_addresses:
        transformed_terms.append(
            "source IP destination IP address "
            + " ".join(ip_addresses)
        )

    # 2. Detect network event IDs
    event_ids = re.findall(
        r"\bNET\d+\b",
        original_query,
        re.IGNORECASE
    )

    if event_ids:
        transformed_terms.append(
            "network event event_id event details "
            + " ".join(event_ids)
        )

    # 3. Expand account-related queries
    if any(term in query_lower for term in [
        "account",
        "username",
        "target user",
        "which user",
        "who was targeted"
    ]):
        transformed_terms.append(
            "target username affected account "
            "login account authentication"
        )

    # 4. Expand login-related queries
    if any(term in query_lower for term in [
        "login",
        "authentication",
        "password",
        "failed attempt"
    ]):
        transformed_terms.append(
            "failed login attempts authentication failures "
            "account access"
        )

    # 5. Expand brute-force-related queries
    if any(term in query_lower for term in [
        "brute force",
        "repeated attempts",
        "multiple attempts"
    ]):
        transformed_terms.append(
            "brute force attack repeated authentication attempts"
        )

    # 6. Expand network-related queries
    if any(term in query_lower for term in [
        "network",
        "connection",
        "traffic",
        "event",
        "port",
        "protocol"
    ]):
        transformed_terms.append(
            "network events event_id suspicious connections "
            "source_ip destination_ip ports protocols"
        )

    # 7. Expand timestamp-related queries
    if any(term in query_lower for term in [
        "when",
        "time",
        "timestamp",
        "timeline",
        "occurred"
    ]):
        transformed_terms.append(
            "event timestamp date time range"
        )

    # 8. Expand threat intelligence queries
    if any(term in query_lower for term in [
        "threat",
        "attack",
        "suspicious",
        "malicious"
    ]):
        transformed_terms.append(
            "cybersecurity threat intelligence security incidents"
        )

    # 9. Build transformed query
    expanded_query = " ".join(transformed_terms)

    transformed_query = original_query

    if expanded_query:
        transformed_query += " " + expanded_query

    return transformed_query


if __name__ == "__main__":

    test_queries = [
        "Why is 198.51.100.23 suspicious?",
        "Which account did it target?",
        "What was the related network event?",
        "Explain event NET001",
        "When did the network event occur?"
    ]

    print("\n========== CYBERSHIELD AI ==========")
    print("          QUERY TRANSFORMATION")
    print("====================================")

    for query in test_queries:

        new_query = transform_query(query)

        print("\nOriginal Query:")
        print(query)

        print("\nTransformed Query:")
        print(new_query)

        print("------------------------------------")

    print("\nQuery transformation completed successfully!")
