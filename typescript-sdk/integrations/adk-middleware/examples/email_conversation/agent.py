import requests
from typing import Optional
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models import LlmResponse, LlmRequest
from google.adk.agents.callback_context import CallbackContext
from .tools import prepare_email_for_approval_tool
from google.adk.tools import LongRunningFunctionTool


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
- When a user asks to send a conversation to someone (e.g., "send conversation to john", "email to benny", "send conversation to john and sarah", "email to benny, alex, and lisa"), you should:
  1. Extract ALL recipient's name from the request.
  2. ALWAYS first lookup the email address using the list of known users provided in the system context (see === AVAILABLE USERS ===). Match the name case-insensitively if an exact match isn't found initially. If multiple users have the same name, ask the user to specify which one (e.g., by email or full name if available).
  3. If the name is not found in the provided list, you MAY ask the user directly for the email address.
  4. Access the conversation history and create a clear summary.
  5. Call the `prepare_email_for_approval_tool` tool with ALL recipients to show editable email components.
  6. Wait for explicit user approval - the user will either click "Send Email" button to approve and send the emails, or "Cancel" button to reject the operation. Respond according to the function response.

**CRITICAL: Tool Output Structure**
When calling the `prepare_email_for_approval_tool` tool, you MUST structure the output exactly as follows:

```json
{
  "recipients": [
    {
      "name": "John Doe", 
      "email": "john.doe@company.com"
    },
    {
      "name": "Sarah Smith",
      "email": "sarah.smith@company.com"
    }
  ],
  "conversation_summary": "## Conversation Summary\n\n[Your detailed summary here]\n\n### Key Points:\n- Point 1\n- Point 2\n\n### Next Steps:\n- Action 1\n- Action 2"
}
```

**Recipients Array Requirements:**
- MUST be an array of objects, even for single recipient
- Each recipient object MUST have both "name" and "email" fields
- Names should be the full names from the user database when available
- Emails must be valid email addresses

**Conversation Summary Requirements:**
- Create a professional, well-structured summary
- Use markdown formatting for clarity
- Include key discussion points and decisions
- Add next steps or action items when relevant
- Make it comprehensive but concise

**Conversation Handling:**
- You have full access to the conversation history.
- Create a well-structured summary that captures the key points.
- Make the summary professional and easy to understand.
- Focus on the most important information and decisions.

**Email Process:**
- Always show clear "From" and "To" fields.
- Make the email body editable so users can modify it before sending.
- Use "ask-benny@aretec.ai" as the sender email and "SLAM" as the sender name.
- Support adding/removing recipients in the approval interface.
- Wait for explicit user approval before considering the task complete.
- Provide detailed status for each recipient (success/failure).

**Example Usage:**
- "Send this conversation to john and sarah" → Look up both names, create recipients array
- "Email the team: alex, ben, lisa" → Find all three emails, prepare for bulk sending
- "Send to John" → Single recipient (backward compatibility)

**Key Guidelines:**
- Prioritize the list of users injected into the system prompt (=== AVAILABLE USERS ===) for finding recipient emails.
- Be concise but comprehensive in your summaries.
- Handle cases where a recipient's email is not immediately known.
- Provide clear feedback at each step.
- ALWAYS call the `prepare_email_for_approval_tool` tool with the exact structure shown above using ONLY "recipients" and "conversation_summary" parameters.
- Only call tools when you have at least one valid recipient with both name and email.
- NEVER use recipient_name, recipient_email, or any other parameter names.

**IMPORTANT:** You MUST call the `prepare_email_for_approval_tool` tool every time a user requests to send an email, using ONLY the "recipients" array format shown above. NEVER use recipient_name or recipient_email parameters.
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        top_p=0.9,
        top_k=40
    ),
    disallow_transfer_to_peers=True,
    tools=[LongRunningFunctionTool(prepare_email_for_approval_tool)],
    before_model_callback=inject_user_emails_to_email_agent,
)