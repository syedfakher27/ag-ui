from ..team_analysis import fetch_team_official_name , fetch_team_name
from .tools import text2sql_query_player_advance_stats , text2sql_query_core_stats
from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from ..research_agent.agent import research_agent
from google.genai import types


research_agent_tool = agent_tool.AgentTool(agent=research_agent)

player_stats_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='team_gap_analysis_agent',
    description="**Player Stats Agent** - Fetch the stats of the players from database and validate it from internet",
    instruction="""
""",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,  # Lower temperature for more consistent analytical output
        top_p=0.9,
        top_k=40
    ),
    disallow_transfer_to_peers=True,
    # before_model_callback=team_analysis_modifier,
    tools=[fetch_team_official_name, fetch_team_name, text2sql_query_player_advance_stats , text2sql_query_core_stats],  # Order matters: fetch_team_name will be called first
    sub_agents=[research_agent_tool]
)