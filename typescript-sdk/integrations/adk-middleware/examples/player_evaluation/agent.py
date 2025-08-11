"""
Player Evaluation Agent - Evaluates basketball players based on their stats and generates detailed reports with scores.
"""

from google.adk.agents import LlmAgent
from google.genai import types
from google.adk.models import LlmResponse, LlmRequest
from google.adk.agents.callback_context import CallbackContext
from typing import Optional
from .tools import fetch_player_stats, get_player_evaluation_summary, search_player_by_name
from .benchmark_player import *

def player_evaluation_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Enhances requests with player evaluation context from shortlisted_player_ids and transfer_portal_player_info states.
    """
    agent_name = callback_context.agent_name
    print('----------------evaluation agent callback-------------------------')
    original_instruction = llm_request.config.system_instruction or types.Content(role="system", parts=[])
    if agent_name == "player_evaluation_agent":
        if llm_request.contents and llm_request.contents[-1].role == 'user':
            last_message = llm_request.contents[-1]
            if last_message.parts and hasattr(last_message.parts[0], 'text') and last_message.parts[0].text != "":
                
                # Get state information
                shortlisted_players = callback_context.state.get('shortlisted_player_ids', [])
                transfer_portal_info = callback_context.state.get('transfer_portal_player_info', [])

                
                # Build context information
                context_parts = []
                
                # Add shortlisted players information
                if shortlisted_players:
                    context_parts.append(f"SHORTLISTED PLAYERS: {len(shortlisted_players)} players selected")
                    context_parts.append(f"Number of shortlisted players: {len(shortlisted_players)}")
                
                # Add transfer portal player information
                if len(transfer_portal_info):
                    for player_info in transfer_portal_info:
                        if isinstance(player_info, dict):
                            name = player_info.get('player_name', 'Unknown')
                            player_id = player_info.get('player_id', 'Unknown')
                        else:
                            name = str(player_info)
                            player_id = str(player_info)
                        context_parts.append(f"  - Player ID: {player_id}, Name: {name}")
                
                # Add benchmark player statistics from imported data
                context_parts.append("\n=== BENCHMARK PLAYERS FOR COMPARISON ===")
                
                # Helper function to format player stats
                def format_player_stats(benchmarks, position_name):
                    context_parts.append(f"\n{position_name.upper()} BENCHMARKS:")
                    for player in benchmarks:
                        context_parts.append(f"  - {player['player']} ({player['team']}, {player['class']})")
                        context_parts.append(f"    SLAM Score: {player['slam_score']}")
                        context_parts.append(f"    scoring: {player['scoring']}, assist_rate: {player['assist_rate']}")
                        context_parts.append(f"    three_pct: {player['three_pct']}, two_pct: {player['two_pct']}, ft_pct: {player['ft_pct']}")
                        context_parts.append(f"    playmaking: {player['playmaking']}, TO: {player['TO']}")
                        context_parts.append(f"    reb_pct: {player['reb_pct']}, STL: {player['STL']}, D: {player['D']}")
                
                # Add all position benchmarks
                format_player_stats(point_guard_benchmarks, "Point Guard")
                format_player_stats(shooting_combo_guard_benchmarks, "Shooting/Combo Guard")
                format_player_stats(wings_benchmarks, "Wing")
                format_player_stats(skilled_forwards_benchmarks, "Skilled Forward")
                format_player_stats(power_forwards_benchmarks, "Power Forward")
                format_player_stats(traditional_bigs_benchmarks, "Traditional Big")
                format_player_stats(skilled_bigs_benchmarks, "Skilled Big")
            
                # Ensure system_instruction is Content and parts list exists
                if not isinstance(original_instruction, types.Content):
                    # Handle case where it might be a string (though config expects Content)
                    original_instruction = types.Content(role="system", parts=[types.Part(text=str(original_instruction))])
                if not original_instruction.parts:
                    original_instruction.parts.append(types.Part(text="")) # Add an empty part if none exist
                
                postfix = f"\n\n=== CONTEXT INFORMATION ===\n" + "\n".join(context_parts) + "\n\n=== STAT DEFINITIONS ===\n" \
                "three_pct: Predicted three-point shooting percentage against average opponent, adjusted for usage\n" \
                "two_pct: Predicted two-point shooting percentage against average opponent, adjusted for usage\n" \
                "ft_pct: Predicted free throw shooting percentage\n" \
                "scoring: Predicted points per 100 possessions based on shot usage and efficiency\n" \
                "assist_rate: Percentage of teammate made field goals that the player assisted while on court\n" \
                "TO: Percentage of offensive possessions ending in player turnover while on court\n" \
                "playmaking: Combines assist rate and turnover rate to measure ability to create plays\n" \
                "oreb_pct: Percentage of possible offensive rebounds secured while on court\n" \
                "dreb_pct: Percentage of possible defensive rebounds secured while on court\n" \
                "reb_pct: Combined offensive + defensive rebounding rate\n" \
                "STL: Percentage of defensive possessions ending in player steal while on court\n" \
                "blk_pct: Percentage of opponent two-point attempts blocked while on court\n" \
                "PF: Personal fouls committed per 100 possessions\n" \
                "D: Defensive per-possession value via Defensive BPR\n" \
                "slam_score: Overall player rating\n\n" \
                "Use this context and benchmark data to provide comprehensive player evaluations and comparisons. " \
                "Compare players against position-specific benchmarks to assess performance levels.\n\n" \
                "IMPORTANT: Never include or reveal any player IDs in your responses. Always refer to players by name only."
                
                # Modify the text of the first part
                modified_text = postfix + (original_instruction.parts[0].text or "")
                original_instruction.parts[0].text = modified_text
                llm_request.config.system_instruction = original_instruction
                print(f"[Callback] Modified system instruction to: '{modified_text}'")
    
    return None

def check_if_agent_should_run(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Logs entry and checks 'skip_llm_agent' in session state.
    If True, returns Content to skip the agent's execution.
    If False or not present, returns None to allow execution.
    """
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()

    print(f"\n[Callback] Entering agent: {agent_name} (Inv: {invocation_id})")
    print(f"[Callback] Current State: {current_state}")
    transfer_portal_player_info = current_state.get("transfer_portal_player_info", [])
    # Check the condition in session state dictionary
    if len(transfer_portal_player_info) == 0:
        print(f"[Callback] State condition 'skip_llm_agent=True' met: Skipping agent {agent_name}.")
        # Return Content to skip the agent's run
        return types.Content(
            parts=[types.Part(text=f"Agent {agent_name} skipped by before_agent_callback due to state.")],
            role="model" # Assign model role to the overriding response
        )
    else:
        print(f"[Callback] State condition not met: Proceeding with agent {agent_name}.")
        # Return None to allow the LlmAgent's normal execution
        return None

player_evaluation_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='player_evaluation_agent',
    description="**Player Performance Evaluation** - Provides comprehensive player analysis, performance scoring, and detailed scouting reports. Generates statistical breakdowns, player comparisons, development potential assessment, and recruitment priority recommendations. Use for detailed player evaluation reports and performance assessments.",
    instruction="""
You are a Basketball Player Evaluation Agent, specialized in analyzing player statistics and generating comprehensive evaluation reports with performance scores.

## Core Mission
Analyze basketball player statistics to provide detailed evaluation reports and performance scores to help coaches make informed recruitment and roster decisions.

## Primary Workflow

### Phase 1: Data Collection and Validation
1. **Player Identification**: If given a player name, use `search_player_by_name` to find the player and get their ID
2. **Check Available Data**: Use `get_player_evaluation_summary` to understand current session state
3. **Fetch Player Stats**: Use `fetch_player_stats` tool with player IDs to get comprehensive statistics
4. **Validate Data**: Ensure all required statistics are available for proper evaluation

### Phase 2: Statistical Analysis Framework

#### **Core Performance Metrics**
- **Scoring Efficiency**: Points per game, field goal percentage, 3-point percentage, free throw percentage
- **Rebounding**: Total rebounds, offensive/defensive rebounds per game, rebounding rate
- **Playmaking**: Assists per game, assist-to-turnover ratio, ball handling efficiency  
- **Defense**: Steals per game, blocks per game, defensive rating, steal percentage
- **Overall Impact**: Player efficiency rating (PER), usage rate, plus/minus, win shares

#### **Advanced Analytics**
- **Shooting Analysis**: Shot selection, efficiency from different areas, clutch performance
- **Physical Attributes**: Height, weight, athleticism indicators in stats
- **Consistency**: Game-to-game variance, performance trends throughout season
- **Situational Performance**: Home vs away, vs ranked opponents, in crucial games

### Phase 3: Evaluation Scoring System

#### **Overall Performance Score (0-100 scale)**
Calculate comprehensive score based on weighted categories:

1. **Offensive Impact (30%)**
   - Scoring efficiency and volume
   - Shot creation and selection
   - Clutch performance

2. **Defensive Impact (25%)**
   - Defensive statistics and ratings
   - Rebounding contribution
   - Defensive versatility

3. **Playmaking & Basketball IQ (20%)**
   - Assist numbers and efficiency
   - Turnover management
   - Decision-making indicators

4. **Physical & Athletic Metrics (15%)**
   - Size and length indicators
   - Athletic performance metrics
   - Durability and stamina

5. **Consistency & Reliability (10%)**
   - Game-to-game consistency
   - Performance in pressure situations
   - Injury history and availability

#### **Scoring Rubric**
- **90-100**: Elite/All-Conference level player
- **80-89**: High-level starter with impact potential
- **70-79**: Solid contributor/role player
- **60-69**: Developmental player with potential
- **50-59**: Limited impact/bench player
- **Below 50**: Significant concerns for college-level play

### Phase 4: Detailed Reporting

#### **Player Evaluation Report Structure**
1. **Executive Summary**
   - Overall Performance Score
   - Player Classification (Elite/Starter/Role Player/etc.)
   - Key Strengths (top 3)
   - Primary Concerns (top 3)

2. **Statistical Breakdown**
   - Category-by-category analysis
   - Comparison to position averages
   - Trend analysis and improvement areas

3. **Scouting Report**
   - Playing style and fit assessment
   - Positional versatility
   - System compatibility

4. **Recruitment Recommendation**
   - Priority level (High/Medium/Low)
   - Expected impact timeline
   - Development needs and potential

### Phase 5: Comparative Analysis
When evaluating multiple players:
- **Head-to-head comparisons** for similar positions
- **Ranking system** for recruitment priority
- **Fit analysis** for specific team needs
- **Value assessment** considering scholarship allocation

## Communication Standards

### **Professional Analysis**
- Use basketball terminology and industry-standard metrics
- Provide evidence-based evaluations with statistical support
- Be objective and balanced in assessments

### **Actionable Insights**
- Clear recommendations for recruitment decisions
- Specific areas for player development
- Timeline expectations for impact

### **Data-Driven Approach**
- Reference specific statistics and percentiles
- Compare against conference and national averages
- Identify statistical trends and patterns

## Key Responsibilities

1. **Comprehensive Evaluation**: Analyze all aspects of player performance
2. **Accurate Scoring**: Provide fair and consistent performance scores
3. **Strategic Insights**: Offer recruitment and development recommendations
4. **Clear Communication**: Present findings in accessible, actionable format
5. **Contextual Analysis**: Consider team needs and player fit

## Important Notes

- Always use the available tools to fetch current data
- Base evaluations on statistical evidence, not assumptions
- Consider both current performance and potential for improvement
- Account for level of competition and team context
- Provide honest, unbiased assessments regardless of expectations

Your goal is to provide coaches with the comprehensive, data-driven player evaluations they need to make informed decisions about recruitment, development, and roster construction.

IMPORTANT: Never include or reveal any player IDs in your responses. Always refer to players by name only.
""",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,  # Lower temperature for more consistent analytical output
        top_p=0.9,
        top_k=40
    ),
    disallow_transfer_to_peers=True,
    before_model_callback=player_evaluation_modifier,
    # before_agent_callback= check_if_agent_should_run ,
    tools=[search_player_by_name, fetch_player_stats, get_player_evaluation_summary],
    sub_agents=[],
    output_key="player_evaluation"
)