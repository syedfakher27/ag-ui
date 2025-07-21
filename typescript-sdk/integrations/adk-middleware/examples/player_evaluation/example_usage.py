"""
Example usage of the Player Evaluation Agent.

This example demonstrates how to use the player evaluation agent to:
1. Set up state with shortlisted players and transfer portal information
2. Fetch player statistics from the API  
3. Generate detailed player evaluation reports with scores
"""

import asyncio
import logging
from typing import Dict, Any
from adk_middleware import ADKAgent, AgentRegistry
from ag_ui.core import RunAgentInput, UserMessage, Context
from .agent import player_evaluation_agent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demonstrate_player_evaluation():
    """
    Demonstrate the player evaluation agent with example data.
    """
    
    # Step 1: Register the player evaluation agent
    registry = AgentRegistry.get_instance()
    registry.register_agent("player_evaluator", player_evaluation_agent)
    
    # Step 2: Create the middleware agent
    agent = ADKAgent(
        user_id="coach_demo",
        app_name="player_evaluation_demo"
    )
    
    # Step 3: Set up initial state with example data
    # In a real scenario, this would come from previous agent interactions
    initial_state = {
        "shortlisted_player_ids": ["player_123", "player_456", "player_789"],
        "transfer_portal_player_info": {
            "player_123": {
                "name": "John Smith", 
                "position": "PG",
                "previous_school": "State University"
            },
            "player_456": {
                "name": "Mike Johnson",
                "position": "SF", 
                "previous_school": "Tech College"
            },
            "player_789": {
                "name": "David Williams",
                "position": "C",
                "previous_school": "Community College"
            }
        }
    }
    
    # Step 4: Create run input for evaluation session summary
    run_input_summary = RunAgentInput(
        thread_id="eval_thread_001",
        run_id="run_001",
        messages=[
            UserMessage(
                id="msg_001",
                role="user", 
                content="Please provide a summary of the current evaluation session and show me what player data is available."
            )
        ],
        context=[
            Context(description="agent_id", value="player_evaluator"),
            Context(description="session_type", value="player_evaluation")
        ],
        state=initial_state,
        tools=[],
        forwarded_props={}
    )
    
    print("=== Player Evaluation Session Summary ===")
    print("-" * 50)
    
    async for event in agent.run(run_input_summary):
        handle_event(event)
    
    # Step 5: Fetch player statistics
    run_input_fetch = RunAgentInput(
        thread_id="eval_thread_001", 
        run_id="run_002",
        messages=[
            UserMessage(
                id="msg_002",
                role="user",
                content="Please fetch the player statistics for all shortlisted players so we can evaluate them."
            )
        ],
        context=[
            Context(description="agent_id", value="player_evaluator")
        ],
        state=initial_state,
        tools=[],
        forwarded_props={}
    )
    
    print("\n=== Fetching Player Statistics ===")
    print("-" * 50)
    
    async for event in agent.run(run_input_fetch):
        handle_event(event)
    
    # Step 6: Generate detailed evaluation report
    run_input_evaluate = RunAgentInput(
        thread_id="eval_thread_001",
        run_id="run_003", 
        messages=[
            UserMessage(
                id="msg_003",
                role="user",
                content="""Now that we have the player statistics, please provide a comprehensive evaluation report for each player including:
                
1. Overall performance score (0-100)
2. Detailed statistical analysis
3. Key strengths and weaknesses
4. Recruitment recommendation and priority level
5. Expected impact and development timeline

Please focus on John Smith (player_123) first, then provide comparative analysis of all three players."""
            )
        ],
        context=[
            Context(description="agent_id", value="player_evaluator"),
            Context(description="evaluation_depth", value="comprehensive")
        ],
        state=initial_state,
        tools=[],
        forwarded_props={}
    )
    
    print("\n=== Comprehensive Player Evaluation ===")
    print("-" * 50)
    
    async for event in agent.run(run_input_evaluate):
        handle_event(event)
    
    # Cleanup
    await agent.close()


def handle_event(event):
    """Handle and display AG-UI events."""
    event_type = event.type.value if hasattr(event.type, 'value') else str(event.type)
    
    if event_type == "RUN_STARTED":
        print("🚀 Evaluation started")
    elif event_type == "RUN_FINISHED":
        print("✅ Evaluation completed")
    elif event_type == "RUN_ERROR":
        print(f"❌ Error: {event.message}")
    elif event_type == "TEXT_MESSAGE_START":
        print("📊 Agent: ", end="", flush=True)
    elif event_type == "TEXT_MESSAGE_CONTENT":
        print(event.delta, end="", flush=True)
    elif event_type == "TEXT_MESSAGE_END":
        print()  # New line after message
    elif event_type == "TOOL_CALL_START":
        print(f"🔧 Using tool: {getattr(event, 'tool_name', 'Unknown')}")
    elif event_type == "TOOL_CALL_END":
        print(f"✓ Tool completed")
    else:
        print(f"📋 Event: {event_type}")


async def custom_evaluation_example():
    """
    Example with custom player IDs and evaluation criteria.
    """
    
    print("\n" + "=" * 60)
    print("CUSTOM PLAYER EVALUATION EXAMPLE")
    print("=" * 60)
    
    # Register agent
    registry = AgentRegistry.get_instance()
    registry.register_agent("custom_evaluator", player_evaluation_agent)
    
    # Create agent
    agent = ADKAgent(
        user_id="coach_custom",
        app_name="custom_evaluation"
    )
    
    # Custom state with different players
    custom_state = {
        "shortlisted_player_ids": ["player_001", "player_002"],
        "transfer_portal_player_info": {
            "player_001": {"name": "Alex Rodriguez", "position": "PG"},
            "player_002": {"name": "Chris Thompson", "position": "PF"}
        }
    }
    
    # Evaluation with specific focus
    run_input = RunAgentInput(
        thread_id="custom_thread",
        run_id="custom_001",
        messages=[
            UserMessage(
                id="custom_msg",
                role="user",
                content="""I need a detailed evaluation focusing on:
                1. Leadership potential and basketball IQ
                2. Defensive impact and versatility
                3. Fit for an up-tempo offensive system
                
                Please fetch the stats and provide recommendations for both players."""
            )
        ],
        context=[
            Context(description="agent_id", value="custom_evaluator"),
            Context(description="evaluation_focus", value="leadership_defense_tempo")
        ],
        state=custom_state,
        tools=[],
        forwarded_props={}
    )
    
    async for event in agent.run(run_input):
        handle_event(event)
    
    await agent.close()


if __name__ == "__main__":
    # Run the main demonstration
    asyncio.run(demonstrate_player_evaluation())
    
    # Uncomment to run the custom example
    # asyncio.run(custom_evaluation_example())