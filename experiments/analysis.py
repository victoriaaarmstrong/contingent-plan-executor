

## vibe coded this, might need to change
def count_conversation_length(file_path):
    """
    Counts the number of USER + AGENT conversation pairs in a text file.
    Multiple consecutive AGENT lines before a USER counts as one pair.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    conversation_length = 0
    waiting_for_user = False  # Tracks if an AGENT message has been sent

    for line in lines:
        if line.startswith("AGENT:"):
            waiting_for_user = True  # Agent spoke, now waiting for user
        elif line.startswith("USER:") and waiting_for_user:
            # Found a user reply after one or more agent messages
            conversation_length += 1
            waiting_for_user = False  # Reset until next AGENT message

    return conversation_length

## also straight vibes on this one, need to test and modify!
def find_redundant_questions(file_path):
    """
    Finds AGENT questions that appear more than once (exact text match).
    Returns a dict where keys are the repeated questions and values are their counts.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    agent_lines = [line[7:].strip() for line in lines if line.startswith("AGENT:")]

    question_counts = {}
    for question in agent_lines:
        question_counts[question] = question_counts.get(question, 0) + 1

    # Filter only those that appear more than once
    redundant_questions = {q: c for q, c in question_counts.items() if c > 1}

    return redundant_questions