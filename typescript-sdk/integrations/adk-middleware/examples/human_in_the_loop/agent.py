
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
from ..team_analysis.agent import team_gap_analysis_agent
from ..player_evaluation.agent import player_evaluation_agent
from .. email_conversation.agent import email_agent
from ..research_agent.agent import research_agent
from ..video_search_agent.agent import video_analysis_agent
from ..player_development_agent.agent import player_development_agent
from ..transfer_portal_agent.agent import transfer_portal_agent
from google.adk.planners import PlanReActPlanner 

from ..team_requirements_agent.agent import team_requirements_agent
from ..player_stats_agent.agents import player_stats_agent
from .mbb_glossary import mbb_metrics
planner = PlanReActPlanner()

# from dotenv import load_dotenv
# load_dotenv()
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
                web_news_context = callback_context.state.get('web_news', 'No research data available')
                team_requirements_context = callback_context.state.get('team_requirements', 'No team requirements data available')
                modified_user_text = original_text + f"\n here are the current filters state for the required players {callback_context.state.get('filters')}\n\n Here is the summary of the current URI team gap analsyis report\n\n##Team Gap Analysis:\n{callback_context.state.get('team_gap_analysis')}\n\n##Web Research Findings:\n{web_news_context}\n\n##Team Requirements and Performance Criteria:\n{team_requirements_context}\n\nIMPORTANT: Never include or reveal any player IDs in your responses. Always refer to players by name only."
                # Update the message content
                last_message.parts[0].text = modified_user_text
                if not isinstance(original_instruction, types.Content):
                    # Handle case where it might be a string (though config expects Content)
                    original_instruction = types.Content(role="system", parts=[types.Part(text=str(original_instruction))])

    return None





research_agent_tool = agent_tool.AgentTool(agent=research_agent)




basketball_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='BasketballAgent',
    description="""This is a **Basketball Agent** that serves as an intelligent dispatcher for basketball team analysis and player evaluation based on stats and recruitment queries. 

**Core Function**: Analyzes user requests and routes them to the most appropriate specialized sub-agent based on the specific nature of their basketball-related needs.

**Available Routing Options**:
- **Team Gap Analysis** - Evaluates team rosters, identifies strengths/weaknesses, and assesses strategic needs
- **Transfer Portal Agent** - Searches transfer portal and creates targeted player recommendations based on criteria
- **Player Evaluation** - Provides comprehensive player performance analysis, scoring, and detailed scouting reports
- **Email Communication** - Handles sharing of conversation summaries and reports via email
- **Research** - Conducts internet research on basketball topics, trends, and external information
- **Video Analysis** - Searches and analyzes sports videos, player highlights, game footage, and performance content
- **Team Requirements** - Analyzes team performance standards, coaching expectations, and recruitment criteria
- **Player Training & Physical Development** - Analyzes player workout stats, strength metrics, athletic testing, and physical progression over time
- **Player Statistics** - Fetches, analyzes, and validates player statistics from database and external sources

**Intelligence**: Uses contextual analysis to determine user intent and route queries to the specialist best equipped to provide comprehensive, actionable assistance. Handles complex multi-step workflows and maintains context across agent handoffs for seamless user experience.
""",
    instruction="""
You are a Basketball Recruitment Router Agent that intelligently routes basketball-related queries to specialized sub-agents based on request type.

## Routing Logic

**team_gap_analysis_agent** - Route when user asks about:
- Team roster analysis, performance evaluation, gaps assessment
- Team strengths/weaknesses, strategic needs, coaching insights
- Keywords: "team analysis", "gaps", "roster evaluation", "team needs"

**transfer_portal_agent** - Route when user asks about:
- Finding transfer portal players, creating shortlists, player recommendations
- Position-specific searches, statistical criteria filtering
- Keywords: "transfer portal", "find players", "shortlist", "recruit"

**player_evaluation_agent** - Route when user asks about:
- Comprehensive player analysis, performance scores, detailed evaluations
- Player comparisons, scouting reports, development potential
- Keywords: "evaluate [player]", "player report", "analysis", "assessment"

**email_agent** - Route when user asks about:
- Sending conversation summaries, sharing reports via email
- Keywords: "email to", "send to", "share with", specific recipient names

**team_requirements_agent** - Route when user asks about:
- Team performance criteria, coaching standards, recruitment requirements
- Keywords: "team requirements", "performance criteria", "coaching standards"

**research_agent_tool** - Only Call this tool when user asks about this explicitly to either use research_agent_tool or ask the following type of questions:
- Information that need to be fetched from internet
- User has provided a url to fetch the information
- Keywords: "internet", "website", "link"

**video_analysis_agent** - Route when user asks about:
- Finding sports videos, player highlights, game footage, training videos
- Video analysis, player performance in videos, game breakdowns
- Searching by player name, team, sport, or video type
- Visual scouting, technique analysis, gameplay evaluation
- Keywords: "video", "highlights", "game footage", "performance video"
- Examples: "Show me John Doe highlights", "Find basketball training videos", "Clemson game footage"

**player_development_agent** - Route when user asks about:
- Player training stats, physical strength, workout performance, athletic testing
- Progression over time, combine results, vertical jump, bench press
- Physical development, measurements, or athletic testing data
- Keywords: "workout", "training stats", "strength", "vertical jump", "bench press", "physical progress", "how strong is X?", "has X improved?"
- Examples: "Show me Jonah Hinton vertical jump progression over the last year", "Compare the physical development of Hinton and Rivera", "Analyze improvement in Alex Crawford stats"

**player_stats_agent** - Route when user asks about:
- Player statistics, game performance metrics, statistical analysis
- Core stats (points, rebounds, assists) and advanced metrics (PER, usage rate, efficiency)
- Team-filtered player statistics, statistical comparisons between players
- Validation of player statistics from authoritative sources
- Keywords: "player stats", "statistics", "performance metrics", "PPG", "rebounds", "assists", "shooting percentage"
- Examples: "Show me John Smith's stats", "Compare player statistics", "Get Lakers players stats", "Validate these stats"

## Communication Protocol
1. Acknowledge the user's request
2. Briefly explain routing decision
3. Set expectations for specialist response
4. Transfer complete context to sub-agent

## Important Notes
- Never reveal player IDs, use names only
- For email confirmations, simply state success/cancellation without details
- Handle hybrid queries by sequencing appropriate agents
- Maintain context continuity for follow-up queries

""",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.4,  # Balanced temperature for routing decisions
        top_p=0.9,
        top_k=40
    ),
    before_model_callback=simple_before_model_modifier,
    # planner=planner,
    tools=[research_agent_tool],
    sub_agents=[team_gap_analysis_agent , transfer_portal_agent , player_evaluation_agent, email_agent, team_requirements_agent, video_analysis_agent, player_development_agent, player_stats_agent]
)