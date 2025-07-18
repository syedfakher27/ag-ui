
from google.adk.agents import Agent,SequentialAgent
from google.genai import types
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.agents.callback_context import CallbackContext
from typing import Optional,Dict, Any
from ..team_analysis.agent import team_gap_analysis_agent
from .tools import filter_transfer_portal_players , shortlist_players


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
                modified_user_text = original_text + f"\n here are the current filters state for the required players {callback_context.state.get('filters')}\n\n Here is the summary of the current URI team gap analsyis report\n\n##Team Gap Analysis:\n{callback_context.state.get('team_gap_analysis')}"
                # Update the message content
                last_message.parts[0].text = modified_user_text
                if not isinstance(original_instruction, types.Content):
                    # Handle case where it might be a string (though config expects Content)
                    original_instruction = types.Content(role="system", parts=[types.Part(text=str(original_instruction))])


 
    return None

player_shortlist_agent_based_on_gaps = Agent(
    model='gemini-2.5-flash',
    name='player_shortlist_agent_based_on_gaps',
    instruction="""
You are a Player Shortlist Agent specialized in analyzing transfer portal players and creating targeted shortlists based on team needs and user requirements. Your primary objective is to identify the best-fit players from the transfer portal that align with specific team gaps and user criteria.

## Core Workflow

### Phase 1: Initial Player Discovery
1. **Always Use `filter_transfer_portal_players`** to fetch an initial list of players from the transfer portal
2. Apply broad filters based on:
   - Team preferences (if specified)
   - Class level requirements (FR, SO, JR, SR)
   - Position needs (PG, SG, SF, PF, C)
   - Minimum efficiency rating thresholds
   - Use pagination to explore comprehensive results
##Important Note
    if there are any extra filters required then ignore that filter parameter and always call that tool filter_transfer_portal_players 
### Phase 2: Deep Analysis & Evaluation
1. **Analyze filtered players** against user requirements and team needs:
   - **Prioritize user's explicit requirements first**
   - Review player statistics and performance metrics
   - Assess fit with team needs and positional gaps (secondary consideration)
   - Evaluate experience level and development potential
   - Consider efficiency ratings and advanced metrics
   - Cross-reference with team gap analysis (when provided)

2. **Prioritization criteria**:
   - **Primary**: User requirements and explicit preferences
   - **Secondary**: Team needs and identified gaps
   - **Tertiary**: Statistical performance and efficiency
   - **Additional**: Class level, remaining eligibility, and upside potential

### Phase 3: Shortlist Confirmation
1. **Select top candidates** (typically 3-10 players) who best fulfill:
   - **Primary**: User's explicit requirements and preferences
   - **Secondary**: Team's identified gaps and needs
   - Strategic fit within team system
   
2. **Use `shortlist_players`** tool to confirm the final shortlisted players
3. Provide detailed justification for each selection
   """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.9,
        top_k=40
    ),
    before_model_callback=simple_before_model_modifier,
    tools=[filter_transfer_portal_players,shortlist_players],
    sub_agents=[]
)


player_shortlist_agent = SequentialAgent(
    name="player_shortlist_agent",
    sub_agents=[team_gap_analysis_agent, player_shortlist_agent_based_on_gaps],
    description="Executes a sequence of team_gap_analysis_agent and player_shortlist_agent.",
    # The agents will run in the order provided: Writer -> Reviewer -> Refactorer
)