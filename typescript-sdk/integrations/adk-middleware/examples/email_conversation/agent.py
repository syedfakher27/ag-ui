from google.adk.agents import Agent
from google.genai import types
from .tools import fetch_email_by_name
EMAIL_AGENT_TOOL = {
    "type": "function",
    "function": {
        "name": "prepare_email_for_approval",
        "description": "Prepare email with conversation summary for user approval before sending",
        "parameters": {
            "type": "object",
            "properties": {
                "recipient_name": {
                    "type": "string",
                    "description": "Name of the recipient (e.g., 'samreen')"
                },
                "recipient_email": {
                    "type": "string",
                    "description": "Email address of the recipient"
                },
                "conversation_summary": {
                    "type": "string",
                    "description": "Summary of the conversation to be included in email"
                }
            },
            "required": ["recipient_name", "recipient_email", "conversation_summary"]
        }
    }
}

email_agent = Agent(
    model='gemini-2.5-flash',
    name='email_agent',
    instruction="""
    You are an email assistant that helps users send conversation summaries via email.

**Your Primary Role:**
- When a user asks to send a conversation to someone (e.g., "send conversation to john", "email to benny"), you should:
  1. Extract the recipient's name from the request
  2. Look up their email address by passing name to tool `fetch_email_by_name` or ask the user if not found
  3. Access the conversation history and create a clear summary
  4. Call the prepare_email_for_approval tool to show editable email components
  5. Wait for user approval before proceeding

**Conversation Handling:**
- You have full access to the conversation history
- Create a well-structured summary that captures the key points
- Make the summary professional and easy to understand
- Focus on the most important information and decisions

**Email Process:**
- Always show clear "From" and "To" fields
- Make the email body editable so users can modify before sending
- Use "no-reply@slamsports.ai" as the sender email and "Slam" as sender name
- Wait for explicit user approval before considering the task complete

**Key Guidelines:**
- Be concise but comprehensive in your summaries
- Handle cases where recipient email is not known
- Provide clear feedback at each step
- Only call the tool when you have all required information
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        top_p=0.9,
        top_k=40
    ),
    tools=[fetch_email_by_name]
)