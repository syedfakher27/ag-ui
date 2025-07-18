import requests
import json
from typing import Dict, List, Optional, Any
import time

def fetch_team_basketball_data(
    university_team:str = "URI"
) -> Dict[str, Any]:
    """
    Fetch combined basketball data for any university team from three different API endpoints.
    This function retrieves comprehensive team context including team information, season games,
    and detailed player statistics.
    
    Args:
        university_team (str): The university team abbreviation (e.g., "URI", "DUKE", "UCLA")
    
    Returns:
        Dict containing combined data from the provided university team
    """
    
    base_url: str = f"https://slam-all-python-359065791766.us-central1.run.app/MBB/{university_team}"
    schema: str = "MBB"
    fetch_all_players: bool = False,
    player_page_size: int = 50
    timeout: int = 30
    
    headers = {
        'accept': 'application/json'
    }
    
    combined_data = {
        'team_info': None,
        'season_games': None,
        'player_data': None,
        'api_status': {
            'team_info_success': False,
            'season_games_success': False,
            'player_data_success': False,
            'errors': []
        }
    }
    
    try:
        # 1. Fetch team information
        print("Fetching team information...")
        team_url = f"{base_url}/seasongames"
        team_params = {'schema': schema}
        
        team_response = requests.get(
            team_url, 
            headers=headers, 
            params=team_params,
            timeout=timeout
        )
        team_response.raise_for_status()
        
        combined_data['team_info'] = team_response.json()
        combined_data['api_status']['team_info_success'] = True
        print(f"✓ Team info fetched successfully")
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching team info: {str(e)}"
        combined_data['api_status']['errors'].append(error_msg)
        print(f"✗ {error_msg}")
    
    try:
        # 2. Fetch all games
        print("Fetching all games...")
        games_url = f"{base_url}/allgames"
        games_params = {'schema': schema}
        
        games_response = requests.get(
            games_url, 
            headers=headers, 
            params=games_params,
            timeout=timeout
        )
        games_response.raise_for_status()
        
        combined_data['season_games'] = games_response.json()
        combined_data['api_status']['season_games_success'] = True
        print(f"✓ Games data fetched successfully ({len(combined_data['season_games'])} games)")
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching games: {str(e)}"
        combined_data['api_status']['errors'].append(error_msg)
        print(f"✗ {error_msg}")
    
    try:
        # 3. Fetch player data
        print("Fetching player data...")
        players_url = f"{base_url}/playerdata"
        
        all_players = []
        page = 1
        
        while True:
            players_params = {
                'page': page,
                'page_size': player_page_size,
                'schema': schema
            }
            
            players_response = requests.get(
                players_url, 
                headers=headers, 
                params=players_params,
                timeout=timeout
            )
            players_response.raise_for_status()
            
            player_data = players_response.json()
            
            # Add current page data
            if 'data' in player_data:
                all_players.extend(player_data['data'])
                
                # Store metadata from first page
                if page == 1:
                    combined_data['player_data'] = {
                        'data': all_players,
                        'total': player_data.get('total', 0),
                        'total_pages': player_data.get('total_pages', 0),
                        'page_size': player_data.get('page_size', player_page_size)
                    }
                
                print(f"✓ Fetched page {page} ({len(player_data['data'])} players)")
                
                # Check if we should continue fetching
                if not fetch_all_players or not player_data.get('has_next', False):
                    break
                if page > 2:
                    break
                    
                page += 1
                # Add small delay to be respectful to the API
                time.sleep(0.1)
            else:
                break
        
        # Update the final data
        if combined_data['player_data']:
            combined_data['player_data']['data'] = all_players
            combined_data['player_data']['pages_fetched'] = page
            
        combined_data['api_status']['player_data_success'] = True
        print(f"✓ Player data fetched successfully ({len(all_players)} total players)")
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching player data: {str(e)}"
        combined_data['api_status']['errors'].append(error_msg)
        print(f"✗ {error_msg}")
    
    # Add summary statistics
    combined_data['summary'] = {
        'total_apis_called': 3,
        'successful_apis': sum([
            combined_data['api_status']['team_info_success'],
            combined_data['api_status']['season_games_success'],
            combined_data['api_status']['player_data_success']
        ]),
        'total_games': len(combined_data['season_games']) if combined_data['season_games'] else 0,
        'total_players': len(combined_data['player_data']['data']) if combined_data['player_data'] else 0,
        'team_count': len(combined_data['team_info']) if combined_data['team_info'] else 0
    }
    
    return combined_data

# Example usage
if __name__ == "__main__":
    # Fetch first page of player data only
    print("=== Fetching URI Basketball Data (First Page Only) ===")
    data = fetch_team_basketball_data(university_team="URI")
    
    # Print summary
    print("\n=== Summary ===")
    print('data==>',data)
    
    # Uncomment to save data to file
    # save_data_to_file(data)
    
    # Uncomment to fetch ALL player data (this will take longer)
    # print("\n=== Fetching ALL Player Data ===")
    # all_data = fetch_uri_basketball_data(fetch_all_players=True)
    # print(f"Total players (all pages): {all_data['summary']['total_players']}")