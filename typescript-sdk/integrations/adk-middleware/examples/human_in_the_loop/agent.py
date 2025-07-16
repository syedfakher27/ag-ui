
from google.adk.agents import Agent
from google.genai import types
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.agents.callback_context import CallbackContext
from typing import Optional,Dict, Any
from .tools import filter_transfer_portal_players

DEFINE_TASK_TOOL = {
    "type": "function",
    "function": {
        "name": "generate_task_steps",
        "description": "Make up 10 steps (only a couple of words per step) that are required for a task. The step should be in imperative form (i.e. Dig hole, Open door, ...)",
        "parameters": {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "The text of the step in imperative form"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["enabled"],
                                "description": "The status of the step, always 'enabled'"
                            }
                        },
                        "required": ["description", "status"]
                    },
                    "description": "An array of 10 step objects, each containing text and status"
                }
            },
            "required": ["steps"]
        }
    }
}

def weather(city: str):
   """
   Get the current weather condition for a specified city.
   
   Args:
       city (str): The name of the city to get weather information for.
       
   Returns:
       str: The current weather condition. Currently always returns "sunny".
       
   Note:
       This is a placeholder implementation that always returns "sunny" 
       regardless of the actual weather conditions in the specified city.
   """
   print('-----------------calling weather tool-------------------')
   return "rainy"

# --- Define the Callback Function ---
def simple_before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM request or skips the call."""
    agent_name = callback_context.agent_name
    if agent_name == "human_in_loop_agent":
        if llm_request.contents and llm_request.contents[-1].role == 'user':
            last_message = llm_request.contents[-1]
            if last_message.parts and hasattr(last_message.parts[0],'text') and last_message.parts[0].text !="" and last_message.parts[0].function_response.__class__.__name__ != 'FunctionResponse' :
                # Get the original text and add prefix
                original_text = last_message.parts[0].text or ""
                modified_user_text = original_text + f"\n here are the current filters state for the required players {callback_context.state.get('filters')}"
                # Update the message content
                last_message.parts[0].text = modified_user_text

 
    return None

human_in_loop_agent = Agent(
    model='gemini-2.5-flash',
    name='human_in_loop_agent',
    instruction=f"""
        You are a College Basketball Transfer Portal Analysis Assistant. Your primary role is to help coaches, recruiters, and basketball analysts identify and evaluate transfer portal players that match their specific team needs and criteria.

        Your responsibilities include:
        
        1. **Player Search & Filtering**: Use the filter_transfer_portal_players function to search for players based on:
           - Positional needs (PG, SG, SF, PF, C)
           - Playing style compatibility (fast-break, half-court, defensive, etc.)
           - Development timeline (immediate impact, 1-year development, 2-year project)
           - Performance thresholds (minutes, efficiency ratings, rebounds/blocks/assists)
           - Availability status (still available, commitment status, draft intentions)

        2. **Intelligent Recommendations**: 
           - Ask clarifying questions to understand team needs and priorities
           - Suggest appropriate filter criteria based on team context
           - Provide alternative search parameters if initial results are limited

        3. **Analysis & Insights**:
           - Explain why certain players match the specified criteria
           - Highlight key strengths and potential concerns for each player
           - Compare multiple players when presenting options

        4. **Interactive Guidance**:
           - Help users refine their search criteria iteratively
           - Suggest adjustments to filters for better results
           - Provide context on transfer portal trends and timing

        When users ask about transfer portal players, always:
        - Gather sufficient information about their needs before filtering
        - Use the filter_transfer_portal_players function with appropriate parameters
        - Present results in a clear, organized manner
        - Offer to refine the search based on feedback

        Be conversational, knowledgeable about college basketball, and focused on helping users make informed recruiting decisions.
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.9,
        top_k=40
    ),
    before_model_callback=simple_before_model_modifier,
    tools=[filter_transfer_portal_players],
    sub_agents=[]
)