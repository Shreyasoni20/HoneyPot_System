def generate_agent_reply(user_text: str):
    replies = [
        "Why is my account being suspended?",
        "Can you explain the issue?",
        "What verification is needed?",
        "I already submitted details earlier."
    ]
    return replies[hash(user_text) % len(replies)]