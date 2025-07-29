"""
Tools for player evaluation agent - fetches player stats from API and provides evaluation capabilities.
"""

import requests
import logging
from typing import Dict, List, Any, Optional
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)


def fetch_player_stats(tool_context: ToolContext, player_ids: List[str]) -> Dict[str, Any]:
    """
    Fetch basketball player statistics from the API for evaluation.
    
    Args:
        player_ids: List of player IDs to fetch stats for (e.g., ["player123", "player456"])
    
    Returns:
        Dictionary containing player statistics data or error information
    """
    try:
        if not player_ids:
            return {
                "status": "error",
                "message": "No player IDs provided. Please provide a list of player IDs to fetch stats for.",
                "data": None
            }
        
        # API configuration
        schema = "MBB"
        url = f"https://slam-all-python-359065791766.us-central1.run.app/MBB/tp-players/stats?schema={schema}"
        
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "player_ids": player_ids
        }
        
        logger.info(f"Fetching stats for {len(player_ids)} players: {player_ids}")
        
        # Make the API request
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        player_stats = response.json()
        
        # Store the fetched stats in the tool context state for the agent to use
        current_stats = tool_context.state.get('player_stats', {})
        if isinstance(player_stats, dict):
            current_stats.update(player_stats)
        else:
            # If response is a list, convert to dict using player_id as key
            for stats in player_stats:
                if isinstance(stats, dict) and 'player_id' in stats:
                    current_stats[stats['player_id']] = stats
        
        tool_context.state['player_stats'] = current_stats
        
        # Also update the last_fetched_players for tracking
        tool_context.state['last_fetched_players'] = player_ids
        
        logger.info(f"Successfully fetched stats for {len(player_ids)} players")
        
        return {
            "status": "success",
            "message": f"Successfully fetched player statistics for {len(player_ids)} players",
            "data": player_stats,
            "player_count": len(player_ids)
        }
        
    except requests.exceptions.Timeout:
        error_msg = "Request timeout - the player stats API took too long to respond"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "data": None
        }
        
    except requests.exceptions.ConnectionError:
        error_msg = "Connection error - unable to connect to the player stats API"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "data": None
        }
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "data": None
        }
        
    except Exception as e:
        error_msg = f"Unexpected error fetching player stats: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "data": None
        }


def search_player_by_name(tool_context: ToolContext, player_names: List[str]) -> Dict[str, Any]:
    """
    Search for a player in the transfer portal by name to get their player ID and basic info.
    
    Args:
        player_names: List of the Name of the player to search for (e.g., "[Shelton Williams-Dryden"])
    
    Returns:
        Dictionary containing player information including player_id needed for stats fetching
    """
    try:
        if not len(player_names):
            return {
                "status": "error",
                "message": "Please provide a player name to search for.",
                "data": None
            }
        
        # API configuration for searching players
        schema = "MBB"
        url = f"https://slam-all-python-359065791766.us-central1.run.app/MBB/tp-players/stats?schema={schema}"
        
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "player_ids": [],
            "player_names": player_names,
        }
        
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        player_stats =  response.json()


        # Store the search results in state for later use
        tool_context.state['player_search_results'] = player_stats
        tool_context.state['last_searched_player'] = player_names
        

        return player_stats

        
    except requests.exceptions.Timeout:
        error_msg = "Request timeout - the player search API took too long to respond"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "data": None
        }
        
    except requests.exceptions.ConnectionError:
        error_msg = "Connection error - unable to connect to the player search API"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "data": None
        }
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "data": None
        }
        
    except Exception as e:
        error_msg = f"Unexpected error searching for player: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "data": None
        }


def get_player_evaluation_summary(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Get a summary of the current player evaluation session including available stats and state.
    
    Returns:
        Dictionary containing evaluation session summary
    """
    try:

        shortlisted_players = tool_context.state.get('shortlisted_player_ids', [])
        transfer_portal_info = tool_context.state.get('transfer_portal_player_info', [])
        

        shortlisted_count = len(shortlisted_players)
        transfer_portal_count = len(transfer_portal_info)
        
        # Get player names from transfer portal info
        available_players = []
        for player in transfer_portal_info:
            available_players.append({
                "player_id": player.get('player_id'),
                "name": player.get('player_name', 'Unknown') ,
                "is_shortlisted": player.get('player_id') in shortlisted_players
            })
        
        summary = {
            "status": "success",
            "session_summary": {
                "total_transfer_portal_players": transfer_portal_count,
                "shortlisted_players_count": shortlisted_count,
                "available_players": available_players
            },
            "state_info": {
                "has_transfer_portal_data": bool(transfer_portal_info),
                "has_shortlisted_players": bool(shortlisted_players)
            }
        }
        
        return summary
        
    except Exception as e:
        error_msg = f"Error getting evaluation summary: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "data": None
        }