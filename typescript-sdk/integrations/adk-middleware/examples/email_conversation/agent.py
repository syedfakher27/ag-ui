import requests
from typing import Optional
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models import LlmResponse, LlmRequest
from google.adk.agents.callback_context import CallbackContext

def inject_user_emails_to_email_agent(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Injects list of users (name and email) fetched from API into email_agent's system prompt.
    """
    agent_name = callback_context.agent_name

    if agent_name == "email_agent":
        # Fetch users from the backend API
        try:
            response = requests.get("https://slam-node-backend-359065791766.us-central1.run.app/api/users")
            response.raise_for_status()
            users_data = response.json().get("users", [])
        except Exception as e:
            print(f"[Callback Error] Failed to fetch users: {e}")
            return None

        # Prepare list of name-email pairs
        user_list = [
            f"- Name: {user['name']}, Email: {user['email']}"
            for user in users_data
        ]
        user_context = "\n".join(user_list)

        # Get current system instruction
        original_instruction = llm_request.config.system_instruction or types.Content(role="system", parts=[])

        # Ensure it's a Content object with parts
        if not isinstance(original_instruction, types.Content):
            original_instruction = types.Content(role="system", parts=[types.Part(text=str(original_instruction))])
        if not original_instruction.parts:
            original_instruction.parts.append(types.Part(text=""))

        # Append user context to the system prompt
        postfix = f"\n\n=== AVAILABLE USERS ===\n{user_context}\n\nUse these names and emails when looking for recipient email.\n"
        modified_text = (original_instruction.parts[0].text or "") + postfix

        original_instruction.parts[0].text = modified_text
        llm_request.config.system_instruction = original_instruction

        print("[Callback] Injected user list into email_agent system prompt.")

    return None

email_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='email_agent',
    instruction="""
    You are an email assistant that helps users send conversation summaries via email.

**Your Primary Role:**
- When a user asks to send a conversation to someone (e.g., "send conversation to john", "email to benny"), you should:
  1. Extract the recipient's name from the request.
  2. ALWAYS first lookup the email address using the list of known users provided in the system context (see === AVAILABLE USERS === ). Match the name case-insensitively if an exact match isn't found initially. If multiple users have the same name, ask the user to specify which one (e.g., by email or full name if available).
  3. If the name is not found in the provided list, you MAY ask the user directly for the email address.
  4. Access the conversation history and create a clear summary.
  5. Call the `prepare_email_for_approval` tool to show editable email components.
  6. Wait for explicit user approval before proceeding.

**Conversation Handling:**
- You have full access to the conversation history.
- Create a well-structured summary that captures the key points.
- Make the summary professional and easy to understand.
- Focus on the most important information and decisions.

**Email Process:**
- Always show clear "From" and "To" fields.
- Make the email body editable so users can modify it before sending.
- Use "no-reply@slamsports.ai" as the sender email and "SLAM" as the sender name.
- Wait for explicit user approval before considering the task complete.

**Key Guidelines:**
- Prioritize the list of users injected into the system prompt (=== AVAILABLE USERS ===) for finding recipient emails.
- Be concise but comprehensive in your summaries.
- Handle cases where a recipient's email is not immediately known.
- Provide clear feedback at each step.
- Only call tools when you have all required information.
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        top_p=0.9,
        top_k=40
    ),
    before_model_callback=inject_user_emails_to_email_agent,
)