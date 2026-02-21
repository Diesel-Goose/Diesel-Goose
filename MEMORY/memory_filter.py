def extract_true_memories(conversation_text, llm):
    prompt = f"""
    Extract ONLY long-term true memories from this conversation.
    
    Rules:
    - Only store persistent facts.
    - Ignore temporary or one-time info.
    - Output JSON list.
    
    Conversation:
    {conversation_text}
    """

    response = llm(prompt)
    return parse_json(response)
