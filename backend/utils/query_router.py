def route_query(query: str):

    q = query.lower().strip()

    greeting_keywords = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good evening"
    ]

    agent_keywords = [
        "fetch",
        "get",
        "start",
        "trigger",
        "send email",
        "workflow",
        "subscription",
        "user id"
    ]

    # Greeting route
    if q in greeting_keywords:
        return "greeting"

    # Agent route
    for word in agent_keywords:
        if word in q:
            return "agent"

    # Default route
    return "rag"