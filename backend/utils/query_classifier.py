def is_greeting(query: str):
    greetings = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good evening"
    ]

    q = query.lower().strip()

    return any(q.startswith(g) for g in greetings)