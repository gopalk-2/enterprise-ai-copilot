from langchain_community.llms import Ollama

llm = Ollama(model="mistral", temperature=0)


def summarize_conversation(history):

    if len(history) < 6:
        return None

    conversation_text = ""

    for msg in history:
        conversation_text += f"{msg['role']}: {msg['content']}\n"

    prompt = f"""
    Summarize the following conversation briefly while preserving key facts.

    Conversation:
    {conversation_text}

    Short Summary:
    """

    summary = llm.invoke(prompt)

    return summary