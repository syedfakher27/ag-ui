from google.adk.agents import Agent,SequentialAgent
from google.genai import types
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import agent_tool
from google.adk.tools import google_search,url_context
from typing import Optional,Dict, Any
from google.adk.agents import LlmAgent
from google.adk.planners import PlanReActPlanner 

from .tools import text2sql_query_transfer_portal , shortlist_players
from ..human_in_the_loop.mbb_glossary import mbb_metrics

planner = PlanReActPlanner()

# --- Define the Callback Function ---
def simple_before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM request or skips the call."""
    agent_name = callback_context.agent_name
    if agent_name == "transfer_portal_agent":
        if llm_request.contents and llm_request.contents[-1].role == 'user':
            last_message = llm_request.contents[-1]
            if last_message.parts and hasattr(last_message.parts[0],'text') and last_message.parts[0].text !="" and last_message.parts[0].function_response.__class__.__name__ != 'FunctionResponse' :
                # Get the original text and add prefix
                original_text = last_message.parts[0].text or ""
                modified_user_text = original_text + mbb_metrics
                last_message.parts[0].text = modified_user_text
    return None

transfer_portal_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='transfer_portal_agent',
    description=f"**Transfer Portal Player Discovery** - Searches transfer portal and creates targeted player shortlists based on criteria. Handles player recommendations, position-specific searches, statistical filtering, and availability status. Use for finding players, creating shortlists, or retrieving specific player stats from the transfer portal.",
    instruction=f"""
You are a Player Shortlist Agent specialized in analyzing transfer portal players and creating targeted shortlists based on team needs and user requirements. Your primary objective is to identify the best-fit players from the transfer portal that align with specific team gaps and user criteria.

## Core Workflow

### Phase 1: Initial Player Discovery
1. **Always Use `text2sql_query_transfer_portal`** to execute SQL queries against the `MBB`.`tp_player_view` table
2. Construct SQL queries based on requirements:
   - Team preferences: `WHERE team = 'Team Name'`
   - Class level requirements: `WHERE player_class IN ('FR', 'SO', 'JR', 'SR')`
     * **FR = Freshman**: First-year college student
     * **SO = Sophomore**: Second-year college student  
     * **JR = Junior**: Third-year college student
     * **SR = Senior**: Fourth-year college student
   - Position needs (Valid positions only): `WHERE position IN ('PG', 'SG', 'SF', 'PF', 'C')`
     * **Point Guard (PG)**: Ball-handling, court vision, assist-to-turnover ratio
     * **Shooting Guard (SG)**: Perimeter shooting, defensive pressure, scoring consistency  
     * **Small Forward (SF)**: Versatility, rebounding, transition play
     * **Power Forward (PF)**: Interior presence, rebounding, mid-range shooting
     * **Center (C)**: Paint protection, rim running, post presence
   - Performance thresholds: `WHERE bpr_predicted > X` or `WHERE possessions > X`
   - Commitment Status: 
     * For available players: `WHERE (new_team IS NULL OR new_team = '' OR new_team = 'nan')`
     * For all players: no filter needed
   - Use LIMIT and OFFSET for pagination
   - Always use the full table name: `MBB`.`tp_player_view`
##Important Note
    If the SQL query fails with an error, analyze the error message and create a corrected SQL query, then retry with the fixed query. 
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
   
2. **Use `shortlist_players`** tool to confirm the final shortlisted players or to get the stats of a particular stats by the player name
3. Provide detailed justification for each selection. 
4. Avoid returning only the BPR of a player. ALWAYS include supporting metrics of player stats (e.g., rebounds, assists, shooting %, defensive metrics, etc.) along with BPR, if available.
5. Refer to the Basketball Metrics Glossary {mbb_metrics} when introducing or explaining any advanced metric to ensure clarity and consistency. For example:
"Assist Rate of 27.19% means the player directly facilitated a basket via assist on nearly 27 out of every 100 possessions they were on the court—indicating elite-level playmaking." 
Ensure that each metric is not only reported but interpreted—explain why it matters and how it reflects the player's strengths, weaknesses, or fit within a team system. 

IMPORTANT: Never include or reveal any player IDs in your responses. Always refer to players by name only.
   """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        top_p=0.9,
        top_k=40
    ),
    disallow_transfer_to_peers=True,
    before_model_callback=simple_before_model_modifier,
    tools=[text2sql_query_transfer_portal,shortlist_players],
    sub_agents=[]
)