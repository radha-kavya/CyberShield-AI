import re


def extract_context(chat_history):
    """
    Extract important information from previous conversation messages.
    """

    history_text = " ".join(
        message["content"] for message in chat_history
    )

    # Extract IP addresses
    ip_addresses = re.findall(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        history_text
    )

    # Extract targeted usernames and account names
    username_patterns = [
        r"(?i)\btargeted\s+username\s*(?:is|:)\s*['\"`]?([a-zA-Z0-9_.-]+)",
        r"(?i)\btargeted\s+account\s*(?:is|:)\s*['\"`]?([a-zA-Z0-9_.-]+)",
        r"(?i)\busername\s*(?:is|:)\s*['\"`]?([a-zA-Z0-9_.-]+)"
    ]

    usernames = []

    for pattern in username_patterns:
        usernames.extend(
            re.findall(pattern, history_text)
        )

    # Remove trailing punctuation
    usernames = [
        username.rstrip(".,;:")
        for username in usernames
    ]

    # Extract network event IDs
    event_ids = re.findall(
        r"\bNET\d+\b",
        history_text,
        re.IGNORECASE
    )

    return {
        "ip": ip_addresses[-1] if ip_addresses else None,
        "username": usernames[-1] if usernames else None,
        "event_id": event_ids[-1] if event_ids else None
    }


def contextualize_question(question, chat_history):
    """
    Add previous conversation context to follow-up questions.
    """

    if not chat_history:
        return question

    context = extract_context(chat_history)

    question_lower = question.lower()

    follow_up_words = [
        "it",
        "this ip",
        "that ip",
        "this address",
        "that address",
        "which account",
        "which username",
        "that user",
        "related event",
        "related network event",
        "that event",
        "same ip",
        "what about it"
    ]

    is_follow_up = any(
        word in question_lower
        for word in follow_up_words
    )

    if not is_follow_up:
        return question

    context_parts = []

    if context["ip"]:
        context_parts.append(
            f"IP address: {context['ip']}"
        )

    if context["username"]:
        context_parts.append(
            f"Targeted username: {context['username']}"
        )

    if context["event_id"]:
        context_parts.append(
            f"Related event ID: {context['event_id']}"
        )

    if not context_parts:
        return question

    return (
        f"{question}\n\n"
        f"Previous conversation context: "
        f"{'; '.join(context_parts)}"
    )


def update_chat_history(chat_history, question, answer):
    """
    Store user questions and assistant answers.
    """

    chat_history.append({
        "role": "user",
        "content": question
    })

    chat_history.append({
        "role": "assistant",
        "content": answer
    })

    return chat_history


if __name__ == "__main__":

    chat_history = []

    question1 = "Why is IP 198.51.100.23 suspicious?"

    answer1 = (
        "Three failed login attempts were detected. "
        "The targeted username is 'john'. "
        "The related event is NET001."
    )

    chat_history = update_chat_history(
        chat_history,
        question1,
        answer1
    )

    question2 = "Which account did it target?"

    contextual_question = contextualize_question(
        question2,
        chat_history
    )

    print("\n========== CONVERSATIONAL CONTEXT TEST ==========")

    print("\nExtracted Context:")
    print(extract_context(chat_history))

    print("\nOriginal Question:")
    print(question2)

    print("\nContextualized Question:")
    print(contextual_question)

    # Test the related network event follow-up
    question3 = "What was the related network event?"

    contextual_question3 = contextualize_question(
        question3,
        chat_history
    )

    print("\n========== NETWORK EVENT FOLLOW-UP TEST ==========")

    print("\nOriginal Question:")
    print(question3)

    print("\nContextualized Question:")
    print(contextual_question3)
