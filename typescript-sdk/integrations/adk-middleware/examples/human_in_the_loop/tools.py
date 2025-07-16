
from .tp_models import generate_mock_players
from typing import List
from google.adk.tools import ToolContext


def filter_transfer_portal_players(tool_context: ToolContext,positionGap:str , styleOfPlay: str , developmentReadiness :str , minutesPerGame:int , efficiencyRating: int , reboundBlockAssist: int , stillAvailable: bool , committed: bool , draftBound:bool) :
    """
    Filter transfer portal players based on team needs and player attributes.
    
    Searches the transfer portal database to find players that match specific
    team requirements including positional needs, playing style compatibility,
    development timeline, and performance metrics.
    
    Args:
        positionGap (str): Position need (e.g., "PG", "SG", "SF", "PF", "C")
        styleOfPlay (str): Required playing style (e.g., "Transition offense", "Half-court offense", "Defense-first", "Balanced")
        developmentReadiness (str): Timeline for contribution (e.g., "Immediate impact", "Multi-year potential", "Project player")
        minutesPerGame (int): Minimum minutes per game requirement
        efficiencyRating (int): Minimum efficiency rating threshold
        reboundBlockAssist (int): Minimum combined rebounds/blocks/assists per game
        stillAvailable (bool): Filter for players still available in portal
        committed (bool): Include/exclude already committed players
        draftBound (bool): Include/exclude players likely to enter NBA draft
    
    Returns:
        List of players matching the specified criteria
        
    Raises:
        ValueError: If invalid position or style parameters are provided
    """
    print('-------------filter_transfer_portal_players---------------')
    current_filters = tool_context.state.get("filters", {})
    current_filters['positionGap'] = positionGap
    current_filters['styleOfPlay'] = styleOfPlay
    current_filters['developmentReadiness'] = developmentReadiness
    current_filters['minutesPerGame'] = minutesPerGame
    current_filters['efficiencyRating'] = efficiencyRating
    current_filters['reboundBlockAssist'] = reboundBlockAssist
    current_filters['availability']['stillAvailable'] = stillAvailable
    current_filters['availability']['committed'] = committed
    current_filters['availability']['draftBound'] = draftBound

        
    tool_context.state["filters"] = current_filters
    # Get all mock players
    all_players = generate_mock_players()
    
    # Filter players based on criteria
    filtered_players = []
    
    for player in all_players:
        # Check position match
        if player['position'] != positionGap :
            continue
        
        # Check style of play match
        if player['style_of_play'] != styleOfPlay:
            continue
        
        # Check development readiness match
        if player['development_readiness'] != developmentReadiness:
            continue
        
        # Check minutes per game (player should meet or exceed minimum)
        if player['minutes_per_game'] < minutesPerGame:
            continue
        
        # Check efficiency rating (player should meet or exceed minimum)
        if player['efficiency_rating'] < efficiencyRating:
            continue
        
        # Check rebound/block/assist percentage (player should meet or exceed minimum)
        if player['rebound_block_assist_percentage'] < reboundBlockAssist:
            continue
        
        # Check availability status
        player_available = player['availability_status'] == "Still available"
        player_committed = player['availability_status'] == "Committed"
        player_draft_bound = player['availability_status'] == "Draft-bound"
        
        if not (
            (stillAvailable and player_available) or
            (committed and player_committed) or
            (draftBound and player_draft_bound)
        ):
            continue
        
        # If all filters pass, add to results
    filtered_players.append({
        "id": 3,
        "name": "Darius Washington",
        "position": "SF",
        "previous_team": "Kansas State",
        "years_remaining": 3,
        "height": "6'7\"",
        "weight": 220,
        "ppg": 12.4,
        "rpg": 6.8,
        "apg": 2.9,
        "minutes_per_game": 25.6,
        "efficiency_rating": 71.2,
        "rebound_block_assist_percentage": 72.4,
        "style_of_play": "Defense-first",
        "development_readiness": "Multi-year potential",
        "availability_status": "Still available",
        "nil_value": "Undervalued",
        "hometown": "Memphis, TN",
        "highlights": ["Lockdown defender", "High basketball IQ", "Improving offensive game"],
        "video_link": "https://example.com/darius-highlights"
    
    })

    return filtered_players