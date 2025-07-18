# College Basketball Team Gap Analysis Agent

A comprehensive AI-powered basketball team analysis system built with ADK middleware and Context7 MCP integration. This agent provides detailed gap analysis and recruitment recommendations for college basketball coaches.

## Features

### 🏀 **Comprehensive Team Analysis**
- **Roster Analysis**: Complete breakdown of current players and their statistics
- **Position-by-Position Evaluation**: Detailed analysis of PG, SG, SF, PF, and C positions
- **Statistical Gap Identification**: Identifies weaknesses in offensive and defensive metrics
- **Performance Trends**: Analyzes season-long performance patterns

### 📊 **Advanced Analytics**
- **Efficiency Metrics**: Offensive and defensive efficiency ratings
- **Comparative Analysis**: Benchmarking against conference and national averages
- **Player Development Tracking**: Identifies improvement areas for current roster
- **Depth Chart Analysis**: Evaluates roster depth and vulnerability points

### 🎯 **Recruitment Intelligence**
- **Player Profiles**: Detailed requirements for ideal recruits at each position
- **Priority Rankings**: Identifies critical vs. nice-to-have recruitment needs
- **Timeline Planning**: Short-term and long-term recruitment strategies
- **Character Traits**: Leadership and coachability assessments

## Quick Start

### Basic Usage

```python
import asyncio
from adk_middleware import ADKAgent, AgentRegistry
from ag_ui.core import RunAgentInput, UserMessage, Context
from team_analysis import team_gap_analysis_agent

async def analyze_team():
    # Register the agent
    registry = AgentRegistry.get_instance()
    registry.register_agent("team_analyst", team_gap_analysis_agent)
    
    # Create middleware agent
    agent = ADKAgent(user_id="coach_demo")
    
    # Create analysis request
    run_input = RunAgentInput(
        thread_id="team_analysis_001",
        run_id="analysis_001",
        messages=[
            UserMessage(
                id="request",
                role="user",
                content="Analyze the URI basketball team for roster gaps and recruitment needs."
            )
        ],
        context=[
            Context(description="team_code", value="URI"),
            Context(description="agent_id", value="team_analyst")
        ],
        state={},
        tools=[],
        forwarded_props={}
    )
    
    # Run analysis
    async for event in agent.run(run_input):
        print(f"Event: {event.type}")
    
    await agent.close()

# Run the analysis
asyncio.run(analyze_team())
```

### Example Usage Scripts

The module includes several example scripts:

```bash
# Run comprehensive team analysis
python -m team_analysis.example_usage

# Or import and use specific functions
from team_analysis.example_usage import analyze_single_team, focused_position_analysis

# Analyze a specific team
await analyze_single_team("DUKE")

# Focus on a specific position
await focused_position_analysis("URI", "PG")
```

## API Reference

### Tools

#### `fetch_team_basketball_data(university_team: str)`
Retrieves comprehensive basketball data for any university team.

**Parameters:**
- `university_team` (str): Team abbreviation (e.g., "URI", "DUKE", "UCLA")

**Returns:**
- Dictionary containing team info, season games, and player data

**Example:**
```python
from team_analysis import fetch_team_basketball_data

data = fetch_team_basketball_data("URI")
print(f"Found {data['summary']['total_players']} players")
```

### Agent Configuration

#### `team_gap_analysis_agent`
The main AI agent configured for basketball team analysis.

**Key Features:**
- **Model**: Gemini 2.5 Flash for advanced reasoning
- **Temperature**: 0.3 for consistent analytical output
- **Tools**: Integrated with `fetch_team_basketball_data`
- **Context Enhancement**: Automatic state management for multi-turn conversations

## Analysis Capabilities

### 1. Positional Analysis
- **Point Guard (PG)**: Ball-handling, court vision, assist-to-turnover ratio
- **Shooting Guard (SG)**: Perimeter shooting, defensive pressure, scoring consistency
- **Small Forward (SF)**: Versatility, rebounding, transition play
- **Power Forward (PF)**: Interior presence, rebounding, mid-range shooting
- **Center (C)**: Paint protection, rim running, post presence

### 2. Statistical Metrics
- **Offensive**: Scoring efficiency, 3-point %, free-throw %, assists per game
- **Defensive**: Steals, blocks, defensive rebounding, opponent shooting %
- **Advanced**: Player efficiency rating, usage rate, true shooting percentage
- **Team**: Pace, offensive/defensive efficiency, turnover ratios

### 3. Gap Identification
- **Critical Needs**: Positions with significant performance gaps
- **Depth Concerns**: Areas vulnerable to injury or transfer
- **Future Planning**: Accounting for graduating players and eligibility
- **System Fit**: Compatibility with coaching philosophy and playing style

## Sample Analysis Output

```
🏀 TEAM GAP ANALYSIS: URI Rams

📊 EXECUTIVE SUMMARY
• Critical Need: Backup Point Guard (depth concern)
• Major Gap: Three-point shooting (28.5% vs 35% conference avg)
• Strength: Interior defense (2.1 blocks per game)

📋 POSITION BREAKDOWN
PG: Current starter solid (7.2 APG) but no reliable backup
SG: Scoring inconsistent, need better perimeter shooter
SF: Well-balanced, good depth
PF: Strong rebounding, could improve range
C: Excellent rim protection, limited offensive range

🎯 RECRUITMENT PRIORITIES
1. Combo Guard (PG/SG) - immediate impact transfer
2. Stretch Forward - adds spacing and versatility
3. Shooting Specialist - improves offensive efficiency

📈 STRATEGIC RECOMMENDATIONS
• Focus on perimeter shooting in practice
• Develop backup PG from current roster
• Target transfers with 2+ years eligibility
```

## Integration with Context7 MCP

This agent is designed to work seamlessly with Context7 MCP for enhanced basketball analytics:

- **Real-time Data**: Fetches current team statistics and performance metrics
- **Contextual Analysis**: Maintains conversation state across multiple queries
- **Enhanced Insights**: Leverages MCP's advanced analytical capabilities

## Configuration Options

### Agent Customization
```python
# Modify agent behavior
team_gap_analysis_agent.generate_content_config.temperature = 0.1  # More deterministic
team_gap_analysis_agent.generate_content_config.top_p = 0.8       # Focused responses
```

### State Management
```python
# Enhance with custom state
state = {
    "team_analysis": {
        "analyzed_teams": ["URI", "DUKE"],
        "current_focus": "Recruitment Strategy",
        "priority_positions": ["PG", "SG"]
    }
}
```

## Error Handling

The agent includes comprehensive error handling:
- API timeout management
- Data validation
- Graceful degradation when data is unavailable
- Detailed error logging

## Performance Optimization

- **Caching**: Reduces API calls for repeated team queries
- **Pagination**: Efficiently handles large datasets
- **Async Processing**: Non-blocking operations for better responsiveness

## Support

For questions or issues:
1. Check the example usage scripts
2. Review the ADK middleware documentation
3. Ensure proper Context7 MCP configuration

## License

This module is part of the ADK middleware examples and follows the same licensing terms.