"""
Team Gap Analysis Module

This module provides comprehensive basketball team analysis capabilities using the ADK middleware.
It includes tools for fetching team data and an intelligent agent for gap analysis and recruitment insights.

Key Components:
- fetch_team_basketball_data: Tool for retrieving comprehensive team statistics
- team_gap_analysis_agent: AI agent specialized in basketball team analysis
- example_usage: Demonstration scripts for different analysis scenarios

Usage:
    from team_analysis import team_gap_analysis_agent, fetch_team_basketball_data
    
    # Register and use the agent through ADK middleware
    registry = AgentRegistry.get_instance()
    registry.register_agent("team_analyst", team_gap_analysis_agent)
"""

from .agent import team_gap_analysis_agent
from .tools import fetch_team_basketball_data,fetch_team_official_name,fetch_team_name

__all__ = [
    'team_gap_analysis_agent',
    'fetch_team_basketball_data',
    'fetch_team_name',
    'fetch_team_official_name'
]

__version__ = "1.0.0"
__author__ = "ADK Middleware Team"
__description__ = "College Basketball Team Gap Analysis using ADK and Context7 MCP"