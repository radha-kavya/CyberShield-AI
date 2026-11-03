
from langchain_ollama import ChatOllama


def get_llm():

    llm = ChatOllama(
        model="qwen2.5:3b",
        temperature=0
    )

    return llm


if __name__ == "__main__":

    print("\n========== CYBERSHIELD AI ==========")
    print("       LOCAL LLM CONNECTION")
    print("====================================")

    llm = get_llm()

    response = llm.invoke(
        "Explain repeated failed login attempts "
        "in simple terms in three sentences."
    )

    print("\nQwen 2.5 Response:")
    print(response.content)

    print("\nLocal LLM connection successful!")
