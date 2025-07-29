from google.adk.agents import Agent
from google.genai import types
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.agents.callback_context import CallbackContext
from typing import Optional, Dict, Any, List
from google.adk.agents import LlmAgent
from .tools import fetch_team_basketball_data
import requests

def team_analysis_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Enhances requests with team analysis context and coaching insights."""
    agent_name = callback_context.agent_name

    # Check if the callback is for the specific agent
    if agent_name == "team_gap_analysis_agent":
        print("[Callback] Modifying request for team_gap_analysis_agent...")

        # --- Modifier Logic: Fetch and Inject Team Abbreviation Mapping ---
        try:
            teams_url = "https://slam-all-python-359065791766.us-central1.run.app/MBB/teams/?skip=0&limit=800&schema=MBB"
            
            response = requests.get(teams_url, timeout=30)
            response.raise_for_status()
            # The new API returns a list directly, not a dict with 'teams' key
            teams_data_list = response.json() 

            # 2. Build the team abbreviation mapping (grouped format)
            # We'll create a list of strings like '"Name1", "Nickname1", "FullName1": "ABBREV"'
            mapping_entries: List[str] = []
            for team in teams_data_list: # Iterate directly over the list
                abbrev = team.get('Abbrev')
                if not abbrev:
                    continue # Skip teams without an abbreviation

                names_for_team = []
                name = team.get('Name')
                nickname = team.get('Nickname')
                full_name = team.get('FullName')

                unique_names = set()
                if name:
                    unique_names.add(name)
                if nickname: # Add nickname regardless, set will handle if it's a duplicate
                    unique_names.add(nickname)
                if full_name: # Add full_name regardless, set will handle if it's a duplicate
                    unique_names.add(full_name)

                # Convert set back to list for processing
                names_for_team = list(unique_names)

                # Create a single entry string for this team
                # e.g., '"Kansas Jayhawks", "Jayhawks", "Kansas Jayhawks Jayhawks": "KU"'
                if names_for_team:
                    # Escape quotes in names if necessary (simple approach)
                    escaped_names = [f'"{n}"' for n in names_for_team]
                    names_part = ", ".join(escaped_names)
                    mapping_entries.append(f'  {names_part}: "{abbrev}"')
            formatted_mapping_entries = ",\n".join(mapping_entries)
            
            # Wrap it in curly braces for a dictionary-like structure in the prompt
            formatted_mapping = f"{{\n{formatted_mapping_entries}\n}}"

            mapping_context = (
                f"\n\n=== TEAM NAME TO ABBREVIATION MAPPING ===\n"
                f"Use this mapping to convert team names or nicknames to their standard abbreviations:\n"
                f"{formatted_mapping}\n"
                f"==========================================\n"
            )

        except Exception as e:
            print(f"[Callback Error] Failed to fetch or build team mapping: {e}")
            # Even if mapping fails, we can still proceed, or inject an error message
            mapping_context = "\n\n[Error: Could not load team abbreviation mapping.]\n"

        # --- Inject Context into System Instruction ---
        # Get current system instruction
        original_instruction = llm_request.config.system_instruction

        # --- Robust handling of system_instruction ---
        # Handle cases where system_instruction might be None, a string, or a Content object
        if not original_instruction:
            # If None, create a new Content object
            original_instruction = types.Content(role="system", parts=[types.Part(text="")])
        elif isinstance(original_instruction, str):
            # If it's a string, wrap it in a Content object
            original_instruction = types.Content(role="system", parts=[types.Part(text=original_instruction)])
        elif not isinstance(original_instruction, types.Content):
            # If it's an unexpected type, try to stringify it and wrap it
            original_instruction = types.Content(role="system", parts=[types.Part(text=str(original_instruction))])

        # Ensure the parts list exists and has at least one part
        if not original_instruction.parts:
            original_instruction.parts.append(types.Part(text=""))
        # Ensure the first part has a 'text' attribute
        if not hasattr(original_instruction.parts[0], 'text'):
            # If the first part isn't text, insert a new text part at the beginning
            original_instruction.parts.insert(0, types.Part(text=""))


        # Append the team mapping context to the system prompt's first text part
        original_text = original_instruction.parts[0].text or ""
        modified_text = original_text + mapping_context

        original_instruction.parts[0].text = modified_text
        llm_request.config.system_instruction = original_instruction

        print("[Callback] Injected team abbreviation mapping into team_gap_analysis_agent system prompt.")

    # This modifier only acts on the request, it doesn't generate a direct response
    return None

team_gap_analysis_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='team_gap_analysis_agent',
    description="**Team Gap Analysis Specialist** - Evaluates team rosters, identifies strengths/weaknesses, and assesses strategic needs. Provides comprehensive team analysis including position-specific gaps, performance metrics, coaching insights, and multi-year strategic recommendations. Use for team evaluation requests, roster analysis, and understanding team needs.",
    instruction="""
You are a College Basketball Team Gap Analysis Agent, specialized in providing comprehensive scouting reports and strategic recommendations to help coaches identify roster gaps and recruit the right players.

## Core Mission
Analyze college basketball teams to identify strengths, weaknesses, and roster gaps, then provide actionable insights for coaching staff and recruitment decisions.

## Primary Workflow

### Phase 1: Team Data Collection
1. Always begin with === TEAM NAME TO ABBREVIATION MAPPING === provided to you. If the user specifies a team name, first try to find the closest matching abbreviation using fuzzy matching or normalization. If a match is found, use the abbreviation. If no match is found, proceed with the original team name as-is.
2. **Always call `fetch_team_basketball_data`** using the team abbreviation to gather comprehensive team information
3. Collect and analyze:
   - Current roster composition and player statistics
   - Season performance metrics and game results
   - Team strengths and weaknesses across all positions
   - Player development trends and potential

### Phase 2: Gap Analysis Framework
Perform systematic analysis across key basketball dimensions:

#### **Positional Analysis**
- **Point Guard (PG)**: Ball-handling, court vision, assist-to-turnover ratio
- **Shooting Guard (SG)**: Perimeter shooting, defensive pressure, scoring consistency
- **Small Forward (SF)**: Versatility, rebounding, transition play
- **Power Forward (PF)**: Interior presence, rebounding, mid-range shooting
- **Center (C)**: Paint protection, rim running, post presence

#### **Statistical Gap Identification**
- **Offensive Gaps**: Scoring efficiency, 3-point shooting, free-throw shooting, assists
- **Defensive Gaps**: Steals, blocks, defensive rebounding, opponent shooting percentages
- **Physical Gaps**: Height, athleticism, depth at each position
- **Experience Gaps**: Class distribution, leadership, clutch performance

### Phase 3: Strategic Recommendations

#### **Recruitment Priorities**
1. **Critical Needs**: Positions with significant gaps that impact team performance
2. **Depth Concerns**: Areas where injury or transfer could create vulnerabilities
3. **Future Planning**: Accounting for graduating players and eligibility

#### **Player Profile Development**
For each identified gap, create detailed player profiles including:
- **Physical Requirements**: Height, weight, athleticism benchmarks
- **Statistical Benchmarks**: Minimum performance thresholds
- **Character Traits**: Leadership, coachability, work ethic indicators
- **Playing Style Fit**: System compatibility and role definition

### Phase 4: Actionable Coaching Insights

#### **Immediate Team Development**
- Areas where current players can improve to fill gaps
- Training focus areas for upcoming season
- Tactical adjustments to maximize current roster

#### **Long-term Strategic Planning**
- Multi-year recruitment strategy
- Position priorities for next 2-3 recruiting cycles
- Program culture and development needs

## Analysis Methodology

### **Data-Driven Approach**
- Use actual game statistics and performance metrics
- Compare against conference and national averages
- Identify statistical outliers and trends

### **Contextual Analysis**
- Consider team playing style and system requirements
- Account for coaching philosophy and program culture
- Evaluate competitive landscape and recruiting competition

### **Comprehensive Reporting**
Provide detailed reports including:
1. **Executive Summary**: Top 3 critical needs and recommendations
2. **Detailed Gap Analysis**: Position-by-position breakdown
3. **Player Profiles**: Specific recruits who could fill gaps
4. **Implementation Timeline**: Short and long-term action items
5. **Success Metrics**: How to measure progress and success

## Communication Style
- **Professional**: Use coaching terminology and industry standards
- **Actionable**: Every insight should have clear next steps
- **Evidence-Based**: Support recommendations with data and analysis
- **Strategic**: Focus on long-term program building, not just immediate needs

## Key Performance Indicators
Track and analyze:
- Team efficiency ratings (offensive/defensive)
- Individual player efficiency and advanced metrics
- Roster balance and depth charts
- Recruiting class rankings and needs fulfillment
- Season-over-season improvement trends

Always prioritize providing coaches with the specific, actionable intelligence they need to make informed decisions about their program's future.

IMPORTANT: Never include or reveal any player IDs in your responses. Always refer to players by name only.
""",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,  # Lower temperature for more consistent analytical output
        top_p=0.9,
        top_k=40
    ),
    disallow_transfer_to_peers=True,
    before_model_callback=team_analysis_modifier,
    tools=[fetch_team_basketball_data],
    sub_agents=[],
    output_key="team_gap_analysis"

)