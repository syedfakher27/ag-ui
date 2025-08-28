import requests
import json
from typing import Dict, List, Optional, Any
import time
from .hardcoded_output import PENN_STATE_OUTPUT

def fetch_team_official_name(abbrev: str) -> Dict[str, Any]:
    """
    Fetches the official team name using a team abbreviation via POST request.
    
    Args:
        abbrev (str): The team abbreviation (e.g., URI, KU). Will be uppercased.
    
    Returns:
        Dict with 'team_name' if found, else 'error' or empty 'team_name'.
    """
    try:
        # Uppercase the abbreviation
        abbrev = abbrev.strip().upper()
        if not abbrev:
            return {"error": "No abbreviation provided.", "team_name": ""}

        url = "https://slam-all-python-359065791766.us-central1.run.app/MBB/team-stats-mia/get-team-by-abbrev?schema=MBB"

        response = requests.post(
            url,
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json={"abbrev": abbrev},
            timeout=30
        )

        if response.status_code != 200:
            return {
                "error": f"API error: {response.status_code}", 
                "team_name": ""
            }

        data = response.json()
        team_name = data.get("team_name", "").strip()

        if not team_name:
            return {"team_name": "", "abbrev": abbrev, "error": f"No team found for abbreviation: {abbrev}"}

        return {
            "team_name": team_name,
            "abbrev": abbrev
        }

    except Exception as e:
        return {
            "error": f"Failed to fetch team name: {str(e)}",
            "team_name": ""
        }

def fetch_team_name(team: str):
    """
    Fetch exact team name matches from the API endpoint.
    
    Args:
    team (str): The starting name of the team to find the team matches (e.g., ('Penn','Penn State') for team 'Penn')

    Returns:
        List[str]: List of the exact name of the team (e.g., ('Penn','Penn State') for team 'Penn')
    """
    base_url: str = "https://slam-all-python-359065791766.us-central1.run.app/MBB/team-stats-mia/similar"
    timeout: int = 30
    
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        # Prepare request body
        body = {
            "team": team
        }
        
        # Fetch team name
        print(f"Fetching exact team name for {team}...")
        response = requests.post(
            base_url,
            headers=headers,
            json=body,
            timeout=timeout
        )
        response.raise_for_status()
        data = response.json()
        if data.get('total', 0) > 0 and len(data.get('data', [])) > 0:
            teams = [team_info['team'] for team_info in  data['data']]
            print(f"✓ Team name fetched successfully: {teams}")
            return teams
        else:
            print("✗ No team data found in the response")
            return "No team data found"
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching team name: {str(e)}"
        print(f"✗ {error_msg}")
        return ""

def fetch_team_basketball_data(team_name: str) -> Dict[str, Any]:
    """
    Fetch combined basketball data for a team including team stats and player stats.
    
    Args:
        team_name (str): The exact team name (e.g., "Penn State")
    
    Returns:
        Dict containing combined team stats and player stats data
    """
    base_url: str = "https://slam-all-python-359065791766.us-central1.run.app/MBB"
    timeout: int = 30
    schema: str = "MBB"
    
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    combined_data = {
        'team_stats': None,
        'player_stats': None,
        'api_status': {
            'team_stats_success': False,
            'player_stats_success': False,
            'errors': []
        }
    }
    
    try:
        # 1. Fetch team stats
        print(f"Fetching team stats for {team_name}...")
        team_stats_url = f"{base_url}/team-stats-mia/search-by-teams"
        team_stats_body = {
            "teams": [team_name]
        }
        
        team_stats_response = requests.post(
            team_stats_url,
            headers=headers,
            json=team_stats_body,
            timeout=timeout
        )
        team_stats_response.raise_for_status()
        
        team_stats_data = team_stats_response.json()
        if team_stats_data.get('total', 0) > 0 and len(team_stats_data.get('data', [])) > 0:
            combined_data['team_stats'] = team_stats_data['data'][0]
            combined_data['api_status']['team_stats_success'] = True
            print(f"✓ Team stats fetched successfully")
        else:
            print(f"✗ No team stats found for {team_name}")
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching team stats: {str(e)}"
        combined_data['api_status']['errors'].append(error_msg)
        print(f"✗ {error_msg}")
    
    try:
        # 2. Fetch player stats
        print(f"Fetching player stats for {team_name}...")
        player_stats_url = f"{base_url}/official-roasters/search"
        player_stats_body = {
            "team_name": team_name
        }
        
        player_stats_response = requests.post(
            player_stats_url,
            headers=headers,
            json=player_stats_body,
            timeout=timeout
        )
        player_stats_response.raise_for_status()
        
        player_stats_data = player_stats_response.json()
        if player_stats_data.get('total_players', 0) > 0 and player_stats_data.get('data'):
            combined_data['player_stats'] = player_stats_data['data']
            combined_data['api_status']['player_stats_success'] = True
            print(f"✓ Player stats fetched successfully ({len(player_stats_data['data'])} players)")
        else:
            print(f"✗ No player stats found for {team_name}")
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching player stats: {str(e)}"
        combined_data['api_status']['errors'].append(error_msg)
        print(f"✗ {error_msg}")
    
    # Special handling for Penn State - add hardcoded player data
    if team_name.lower() == "penn state":
        print("Adding hardcoded Penn State player data...")
        # Convert hardcoded data to match API format
        # hardcoded_players = []
        # for player_data in PENN_STATE_OUTPUT[0]:  # Note: Data is nested in a list
        #     if player_data["Name"]:  # Only include players with names
        #         api_format_player = {
        #             "player": player_data["Name"],
        #             "team": "Penn State",
        #             "value_three_pct": str(player_data["value_three_pct"]) if player_data["value_three_pct"] is not None else None,
        #             "value_two_pct": str(player_data["value_two_pct"]) if player_data["value_two_pct"] is not None else None,
        #             "value_ft_pct": str(player_data["value_ft_pct"]) if player_data["value_ft_pct"] is not None else None,
        #             "value_scoring": str(player_data["value_scoring"]) if player_data["value_scoring"] is not None else None,
        #             "value_assist_rate": str(player_data["value_assist_rate"]) if player_data["value_assist_rate"] is not None else None,
        #             "value_TO": str(player_data["value_TO"]) if player_data["value_TO"] is not None else None,
        #             "value_playmaking": str(player_data["value_playmaking"]) if player_data["value_playmaking"] is not None else None,
        #             "value_oreb_pct": str(player_data["value_oreb_pct"]) if player_data["value_oreb_pct"] is not None else None,
        #             "value_dreb_pct": str(player_data["value_dreb_pct"]) if player_data["value_dreb_pct"] is not None else None,
        #             "value_reb_pct": str(player_data["value_reb_pct"]) if player_data["value_reb_pct"] is not None else None,
        #             "value_blk_pct": str(player_data["value_blk_pct"]) if player_data["value_blk_pct"] is not None else None,
        #             "value_STL": str(player_data["value_STL"]) if player_data["value_STL"] is not None else None,
        #             "value_PF": str(player_data["value_PF"]) if player_data["value_PF"] is not None else None,
        #             "value_D": str(player_data["value_D"]) if player_data["value_D"] is not None else None,
        #             "color_three_pct": player_data["color_three_pct"],
        #             "color_two_pct": player_data["color_two_pct"],
        #             "color_ft_pct": player_data["color_ft_pct"],
        #             "color_scoring": player_data["color_scoring"],
        #             "color_assist_rate": player_data["color_assist_rate"],
        #             "color_TO": player_data["color_TO"],
        #             "color_playmaking": player_data["color_playmaking"],
        #             "color_oreb_pct": player_data["color_oreb_pct"],
        #             "color_dreb_pct": player_data["color_dreb_pct"],
        #             "color_blk_pct": player_data["color_blk_pct"],
        #             "color_STL": player_data["color_STL"],
        #             "color_PF": player_data["color_PF"],
        #             "color_D": player_data["color_D"],
        #             # Add any additional fields that might be needed
        #             "player_notes": player_data["players"]  # Adding player notes/description
        #         }
        #         hardcoded_players.append(api_format_player)
        
        # Combine API players with hardcoded players
        if combined_data['player_stats'] is None:
            combined_data['player_stats'] = []
        
        # Add hardcoded players to the existing player stats
        combined_data['player_stats'].extend(PENN_STATE_OUTPUT)
        print(f"✓ Added {len(PENN_STATE_OUTPUT)} hardcoded players")
    
    # Add summary statistics
    combined_data['summary'] = {
        'total_apis_called': 2,
        'successful_apis': sum([
            combined_data['api_status']['team_stats_success'],
            combined_data['api_status']['player_stats_success']
        ]),
        'total_players': len(combined_data['player_stats']) if combined_data['player_stats'] else 0,
        'team_name': team_name,
        'team_rank': combined_data['team_stats'].get('rank') if combined_data['team_stats'] else None,
        'wins': combined_data['team_stats'].get('wins') if combined_data['team_stats'] else None,
        'losses': combined_data['team_stats'].get('losses') if combined_data['team_stats'] else None
    }
    
    return combined_data
# Example usage
if __name__ == "__main__":
    # Test fetch_team_name function
    print("\n=== Fetching Similar Team Name ===")
    # team_name = fetch_team_name("penn state")
    team_name = "penn state"
    print(f"Similar team name: {team_name}")
    
    if team_name:
        # Test fetch_team_basketball_data with the exact team name
        print("\n=== Fetching Team Basketball Data ===")
        data = fetch_team_basketball_data(team_name)
        print("\n=== Summary ===")
        print('data==>', data)
    
    # Print summary
    print("\n=== Summary ===")
    print('Similar team:', team_name)
    
    # Original test code
    # print("\n=== Fetching URI Basketball Data (First Page Only) ===")
    # # Print summary
    # print("\n=== Summary ===")
    # print('data==>', data)
    
    # # Uncomment to save data to file
    # # save_data_to_file(data)
    
    # # Uncomment to fetch ALL player data (this will take longer)
    # # print("\n=== Fetching ALL Player Data ===")
    # # all_data = fetch_uri_basketball_data(fetch_all_players=True)
    # # print(f"Total players (all pages): {all_data['summary']['total_players']}")

# Make both functions available for import
__all__ = ['fetch_team_name', 'fetch_team_basketball_data']