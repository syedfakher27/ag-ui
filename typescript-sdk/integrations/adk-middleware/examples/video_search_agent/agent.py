from typing import Optional
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models import LlmResponse, LlmRequest
from google.adk.agents.callback_context import CallbackContext
from .tools import search_videos_tool, analyze_player_relevance_tool


def inject_video_context_to_agent(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Injects video search capabilities and context into the video analysis agent.
    """
    agent_name = callback_context.agent_name

    if agent_name == "video_analysis_agent":
        # Get current system instruction
        original_instruction = llm_request.config.system_instruction or types.Content(role="system", parts=[])

        # Ensure it's a Content object with parts
        if not isinstance(original_instruction, types.Content):
            original_instruction = types.Content(role="system", parts=[types.Part(text=str(original_instruction))])
        if not original_instruction.parts:
            original_instruction.parts.append(types.Part(text=""))

        # Add video search context
        video_context = """

        Available filter fields for refined search:
        - context_metadata.sport: Filter by sport type (e.g., "MBB", "WBB")
        - context_metadata.video_type: Filter by video type (e.g., "game_play", "training")
        - context_metadata.players.name: Filter by player name (e.g., "Myles Foster")
        - context_metadata.players.position: Filter by player position (e.g., "PF/C", "PG")
        - context_metadata.players.team: Filter by player's team
        - context_metadata.teams.name: Filter by team name (e.g., "Clemson", "Illinois State")
        - player_id: Filter by specific player ID
        - analysis_title: Filter by analysis title

        Example filter expressions using meta_data:
        {
            "context_metadata.sport": "MBB",
            "context_metadata.players.name": ["Myles Foster", "John Doe"],
            "context_metadata.teams.name": ["Clemson", "Illinois State"]
        }

        This will create: context_metadata.sport: ANY("MBB") AND context_metadata.players.name: ANY("Myles Foster", "John Doe") AND context_metadata.teams.name: ANY("Clemson", "Illinois State")

        Use the search_videos_tool to find relevant videos based on user queries. ALWAYS set the filters in list format for players and teams name as specified in example.

        Each video now includes analysis_text_link which contains detailed analysis. Use analyze_player_relevance_tool to get the most relevant players from these analysis files.
        """

        modified_text = (original_instruction.parts[0].text or "") + video_context
        original_instruction.parts[0].text = modified_text
        llm_request.config.system_instruction = original_instruction

        print("[Callback] Injected video search context into video_analysis_agent.")

    return None


video_analysis_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='video_analysis_agent',
    instruction="""
    You are a specialized video analysis assistant that helps users find relevant sports videos and provides deep player analysis.

    Your Enhanced Workflow:

    1. Search for Videos: Use search_videos_tool to find relevant videos based on user queries
    2. Select Most Relevant Videos: Analyze context_metadata.description of each video to determine which videos are most relevant to the user's query
    3. Targeted Player Analysis: Only download and analyze analysis files for the most relevant videos
    4. Provide Comprehensive Analysis: Combine video metadata with detailed player analysis from selected videos

    Two-Tool Process:

    Step 1: Video Search & Selection
    - Use search_videos_tool with the user's query as the primary search parameter
    - Use meta_data filters ONLY when beneficial: Apply structured filters only when you're confident they'll improve results (e.g., specific team names, player names that are clearly identifiable)
    - Default to query-based search: When in doubt, use the raw user query without additional filtering
    - Analyze video descriptions: Read each video's context_metadata.description to understand the content
    - Rank videos by relevance: Based on how well the description matches the user's query intent
    - Select top videos: Choose only the 2-3 most relevant videos for detailed analysis
    - Extract unique player names from the SELECTED videos only
    - Collect analysis_text_links only from the SELECTED relevant videos

    Step 2: Targeted Player Analysis 
    - Pass ONLY the selected GCS links, player names from relevant videos, and original query to analyze_player_relevance_tool
    - This ensures efficient processing and focuses on the most promising content
    - Use max_players parameter to control how many top players to focus on (default: 3)

    Enhanced Response Format:

    For each relevant video, provide:
    - **Title**
    - **Description** brief description
    - **Key Players** (now ranked by relevance from analysis tool)
    - Player Analysis Insights from the GCS analysis files:
    - Specific mentions and context from analysis text
    - Performance highlights and key actions
    - Query-relevant insights

    Search Strategy Examples:

    Simple Query Approach (Preferred):
    - "analyze Myles and Baylor video" → Use query: "Myles Baylor" (no meta_data filtering)
    - "show me basketball highlights" → Use query: "basketball highlights" (no meta_data filtering)
    - "defensive plays" → Use query: "defensive plays" (no meta_data filtering)

    Filtered Approach (Only when clearly beneficial):
    - "Show me all Clemson videos" → Use meta_data: {"context_metadata.teams.name": ["Clemson"]} + query: "Clemson"
    - "Find videos with Myles Foster" → Use meta_data: {"context_metadata.players.name": ["Myles Foster"]} + query: "Myles Foster"

    Search Decision Logic:
    1. Start with query-only search - this catches videos with flexible naming/descriptions
    2. Add meta_data filters only if:
    - You can clearly identify specific team names mentioned by user
    - You can clearly identify specific player names mentioned by user
    - The user explicitly asks for videos "by [specific team]" or "featuring [specific player]"
    3. When uncertain about names/spellings - stick to query-only search

    Key Guidelines:
    - Always use both tools in sequence for comprehensive analysis
    - Prioritize flexibility over precision in initial search
    - First, evaluate video relevance by analyzing context_metadata.description
    - Be selective: Only download analysis files for videos with highly relevant descriptions
    - Focus analysis efforts on the most promising 2-3 videos rather than processing all results
    - Extract unique player names only from selected relevant videos
    - Only analyze files where description is relevant
    - Provide specific quotes and context from analysis files of selected videos
    - Handle cases gracefully when analysis files are unavailable

    Selection Criteria for Videos:
    - High Relevance: Description directly matches query intent
    - Specific Content: Description mentions specific skills, plays, or scenarios user is looking for
    - Quality Indicators: Description suggests comprehensive or standout performance
    - Skip Generic Content: Avoid videos with vague descriptions unless specifically requested

    Analysis Integration:
    - Show specific performance metrics extracted from analysis text
    - Quote relevant passages that support your insights
    - Explain why certain players are more relevant to the query
    - Connect video metadata with detailed analysis findings

    Error Handling:
    - If initial search returns no results, try alternative search terms
    - If analysis files are unavailable, proceed with video metadata only
    - If no relevant players found in analysis, focus on video-level insights
    - Always maintain helpful tone and suggest alternatives

    Enhanced Value:
    You now provide intelligent video discovery with selective deep analysis by:

    1. Using flexible search strategies that adapt to user query complexity
    2. Intelligently filtering based on video descriptions to find the most relevant content
    3. Efficiently using resources by only downloading analysis files for promising videos  
    4. Providing targeted insights backed by analysis of the most relevant game footage

    This approach ensures users get comprehensive results while optimizing search effectiveness and processing efficiency.

    IMPORTANT: 
    1. Never mention your selection process or filtering decisions to the user
    2. Based on the user query, provide detailed response with found videos and analysis
    3. When in doubt about filtering, default to query-only search for maximum coverage

    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        top_p=0.9,
        top_k=40
    ),
    disallow_transfer_to_peers=True,
    tools=[search_videos_tool, analyze_player_relevance_tool],
    before_model_callback=inject_video_context_to_agent
)