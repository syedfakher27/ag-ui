#!/usr/bin/env python3
"""
Team Gap Analysis Agent Example Usage

This example demonstrates how to use the team gap analysis agent to:
1. Analyze college basketball teams
2. Identify roster gaps and weaknesses
3. Generate coaching insights and recruitment recommendations
"""

import asyncio
import logging
from typing import AsyncGenerator

from adk_middleware import ADKAgent, AgentRegistry
from ag_ui.core import RunAgentInput, BaseEvent, Message, UserMessage, Context
from .agent import team_gap_analysis_agent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_event(event: BaseEvent):
    """Handle and display AG-UI events for team analysis."""
    event_type = event.type.value if hasattr(event.type, 'value') else str(event.type)
    
    if event_type == "RUN_STARTED":
        print("🏀 Team Gap Analysis Started")
    elif event_type == "RUN_FINISHED":
        print("✅ Team Gap Analysis Complete")
    elif event_type == "RUN_ERROR":
        print(f"❌ Analysis Error: {event.message}")
    elif event_type == "TEXT_MESSAGE_START":
        print("📊 Analysis: ", end="", flush=True)
    elif event_type == "TEXT_MESSAGE_CONTENT":
        print(event.delta, end="", flush=True)
    elif event_type == "TEXT_MESSAGE_END":
        print()  # New line after message
    elif event_type == "TOOL_CALL_START":
        print(f"🔧 Fetching team data...")
    elif event_type == "TOOL_CALL_END":
        print(f"✓ Data retrieved successfully")
    else:
        print(f"📋 Event: {event_type}")


async def analyze_single_team(team_code: str = "URI"):
    """Analyze a single team for gaps and recruitment needs."""
    
    # Register the team gap analysis agent
    registry = AgentRegistry.get_instance()
    registry.register_agent("team_analyst", team_gap_analysis_agent)
    
    # Create the middleware agent
    agent = ADKAgent(
        user_id="coach_demo",
        app_name="team_gap_analysis"
    )
    
    # Create analysis request
    run_input = RunAgentInput(
        thread_id=f"team_analysis_{team_code}",
        run_id=f"analysis_001",
        messages=[
            UserMessage(
                id="analysis_request",
                role="user",
                content=f"""Please provide a comprehensive gap analysis for the {team_code} basketball team. 
                
                I need:
                1. A detailed breakdown of current roster strengths and weaknesses
                2. Identification of critical gaps at each position
                3. Statistical analysis of team performance metrics
                4. Specific recruitment recommendations with player profiles
                5. Short-term and long-term strategic recommendations
                
                Focus on actionable insights that will help with coaching decisions and recruiting strategy."""
            )
        ],
        context=[
            Context(description="analysis_type", value="comprehensive_gap_analysis"),
            Context(description="team_code", value=team_code),
            Context(description="agent_id", value="team_analyst"),
            Context(description="focus", value="recruitment_strategy")
        ],
        state={
            "team_analysis": {
                "analyzed_teams": [],
                "current_focus": "Gap Analysis and Recruitment"
            }
        },
        tools=[],
        forwarded_props={}
    )
    
    print(f"🏀 Starting comprehensive gap analysis for {team_code}")
    print("=" * 60)
    
    try:
        async for event in agent.run(run_input):
            handle_event(event)
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
    finally:
        await agent.close()


async def compare_multiple_teams(team_codes: list = ["URI", "DUKE", "UCLA"]):
    """Compare multiple teams and provide strategic insights."""
    
    registry = AgentRegistry.get_instance()
    registry.register_agent("team_analyst", team_gap_analysis_agent)
    
    agent = ADKAgent(
        user_id="coach_comparison",
        app_name="multi_team_analysis"
    )
    
    # Analyze each team
    for i, team_code in enumerate(team_codes):
        print(f"\n{'='*60}")
        print(f"ANALYZING TEAM {i+1}: {team_code}")
        print(f"{'='*60}")
        
        run_input = RunAgentInput(
            thread_id=f"comparison_analysis_{team_code}",
            run_id=f"comparison_{i+1:03d}",
            messages=[
                UserMessage(
                    id=f"comparison_request_{i}",
                    role="user",
                    content=f"""Analyze the {team_code} basketball team focusing on:
                    
                    1. Key statistical strengths and weaknesses
                    2. Position-by-position gap analysis
                    3. Comparison to national averages
                    4. Top 3 recruitment priorities
                    
                    Keep the analysis focused and actionable for coaching staff."""
                )
            ],
            context=[
                Context(description="analysis_type", value="comparative_analysis"),
                Context(description="team_code", value=team_code),
                Context(description="agent_id", value="team_analyst")
            ],
            state={
                "team_analysis": {
                    "analyzed_teams": team_codes[:i],
                    "current_focus": f"Comparative Analysis ({i+1}/{len(team_codes)})"
                }
            },
            tools=[],
            forwarded_props={}
        )
        
        try:
            async for event in agent.run(run_input):
                handle_event(event)
        except Exception as e:
            print(f"❌ Error analyzing {team_code}: {e}")
        
        # Small delay between analyses
        await asyncio.sleep(1)
    
    await agent.close()


async def focused_position_analysis(team_code: str = "URI", position: str = "PG"):
    """Perform focused analysis on a specific position."""
    
    registry = AgentRegistry.get_instance()
    registry.register_agent("team_analyst", team_gap_analysis_agent)
    
    agent = ADKAgent(
        user_id="position_analyst",
        app_name="position_analysis"
    )
    
    run_input = RunAgentInput(
        thread_id=f"position_analysis_{team_code}_{position}",
        run_id="position_001",
        messages=[
            UserMessage(
                id="position_request",
                role="user",
                content=f"""I need a detailed analysis of the {position} position for {team_code}. 
                
                Please provide:
                1. Current players at this position and their statistics
                2. Strengths and weaknesses of current {position} players
                3. How this position compares to team needs
                4. Specific recruitment profile for an ideal {position} candidate
                5. Timeline and priority level for filling this position
                
                Be specific about statistics, measurables, and playing style requirements."""
            )
        ],
        context=[
            Context(description="analysis_type", value="position_focused"),
            Context(description="team_code", value=team_code),
            Context(description="target_position", value=position),
            Context(description="agent_id", value="team_analyst")
        ],
        state={
            "team_analysis": {
                "analyzed_teams": [team_code],
                "current_focus": f"{position} Position Analysis"
            }
        },
        tools=[],
        forwarded_props={}
    )
    
    print(f"🏀 Analyzing {position} position for {team_code}")
    print("=" * 50)
    
    try:
        async for event in agent.run(run_input):
            handle_event(event)
    except Exception as e:
        print(f"❌ Error during position analysis: {e}")
    finally:
        await agent.close()


async def main():
    """Main function with different analysis examples."""
    
    print("🏀 College Basketball Team Gap Analysis Agent Demo")
    print("=" * 60)
    
    try:
        # Example 1: Single team comprehensive analysis
        print("\n📊 EXAMPLE 1: Comprehensive Team Analysis")
        await analyze_single_team("URI")
        
        # Example 2: Position-focused analysis
        print("\n📊 EXAMPLE 2: Position-Focused Analysis")
        await focused_position_analysis("URI", "PG")
        
        # Example 3: Multiple team comparison (uncomment to run)
        # print("\n📊 EXAMPLE 3: Multi-Team Comparison")
        # await compare_multiple_teams(["URI", "DUKE"])
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
    
    print("\n🏀 Demo completed!")


if __name__ == "__main__":
    asyncio.run(main())