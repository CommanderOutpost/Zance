CHUNKING_SYSTEM_PROMPT = (
    "Your job is to convert the thought of the master Gypsie and after turn it into text messages."
    "You are to only output a list of dicts and nothing else."
    "It must be valid!"
    "Example Output:\n"
    "[\n"
    "  { 'content': 'The secret to unlocking true happiness', 'delay_seconds': 1 },\n"
    "  { 'content': 'is not what people think.', 'delay_seconds': 3 },\n"
    "  { 'content': 'Most assume it’s wealth, love, or power', 'delay_seconds': 2 },\n"
    "  { 'content': 'but it's actually about mastering your own mind.', 'delay_seconds': 4 }\n"
    "]\n"
    "\n"
    "Ensure that all generated responses follow this structured format, keeping users engaged while delivering information in a dynamic way.\n"
)


def get_chunking_system_prompt():
    return CHUNKING_SYSTEM_PROMPT


def generate_content_prompt(
    user_prompt, user_data, ai_data, master_decision, conversation_history
):
    return (
        f"Conversation History:{conversation_history}\nUser Prompt: {user_prompt}\n"
        f"User Name: {user_data["username"]}\nAI Data: {ai_data}\nMaster Decision: {master_decision}\n"
    )
