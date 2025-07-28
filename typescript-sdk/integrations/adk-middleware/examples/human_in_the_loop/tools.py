from typing import List, Optional, Dict, Any
from google.adk.tools import ToolContext
from urllib.parse import quote
import requests

def filter_transfer_portal_players(
    tool_context: ToolContext,
    class_: Optional[str] = None,
    position: Optional[str] = None,
    efficiencyRating: Optional[int] = None,
    excludeCommitted: Optional[bool] = False,
    page: int = 1,
    page_size: int = 20,
    sort_by: Optional[str] = None,
    limit: Optional[int] = None,
    additional_filter:Optional[str] = ""

):
    """
    Filter transfer portal players based on team needs and player attributes.
    
    Searches the transfer portal database to find players that match specific
    team requirements including team, class, position, and minimum possessions.
    
    Args:
        team (str, optional): Team name to filter by (e.g., "Montana State")
        class_ (str, optional): Class level (e.g., "JR", "SR", "SO", "FR")
        position (str, optional):
            PF - Match: "power forward", "power", "forward" (if "small" not present), "PF", "4"
            PG - Match: "point guard", "point", "guard" (if "shooting" not present), "PG", "1", "primary guard"
            SG - Match: "shooting guard", "shooting", "two guard", "SG", "2", "off guard"
            SF - Match: "small forward", "small", "forward" (if "power" not present), "SF", "3", "wing"
            C - Match: "center", "centre", "C", "5", "big", "pivot"
        efficiencyRating (int, optional): Minimum possessions threshold
        excludeCommitted (bool, optional) : if enabled, then filter players who are not commmitted to any team
        page (int): Page number for pagination (default: 1)
        page_size (int): Number of results per page (default: 20)
        additional_filter (str, optional) : if there is any extra filter use this param like this "rank:80"
    
    Returns:
        dict: Contains filtered players list and pagination info
        
    Raises:
        Exception: If API request fails or invalid parameters are provided
    """
    print('-------------filter_transfer_portal_players---------------')
    schema = "MBB"
    team=None
    # Store current filters in tool context
    current_filters = tool_context.state.get("filters", {})
    # current_filters.update({
    #     'team': team,
    #     'class_': class_,
    #     'position': position,
    #     'min_possessions': efficiencyRating,
    #     'page': page,
    #     'page_size': page_size,
    #     'schema': schema,
    #     'excludeCommitted': excludeCommitted
    # })
    tool_context.state["filters"]["excludeCommitted"] = current_filters.get('excludeCommitted',False)
    

    # Base API URL
    base_url = "https://slam-all-python-359065791766.us-central1.run.app/MBB/tp-players/"
    
    # Build query parameters
    params = []
    
    if team:
        params.append(f"team={quote(team)}")
    
    if class_:
        params.append(f"class={quote(class_)}")
    
    if position:
        params.append(f"position={quote(position)}")
    
    if efficiencyRating is not None:
        params.append(f"min_possessions={efficiencyRating}")
    if excludeCommitted:
        params.append("isavailable=true")
    else:
        params.append("isavailable=false")
    
    # Add pagination parameters
    params.append(f"page={page}")
    params.append(f"page_size={page_size}")
    params.append(f"schema={schema}")
    
    # Construct full URL
    if params:
        url = f"{base_url}?{'&'.join(params)}"
    else:
        url = f"{base_url}?page={page}&page_size={page_size}&schema={schema}"
    
    print(f"API Request URL: {url}")
    # with open('api.txt', 'w') as f:
    #     f.write(url)
    try:
        # Make API request
        headers = {
            'accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse response
        api_response = response.json()
        
        # Extract player data
        players_data = api_response.get('data', [])
        players_info = api_response.get('data', [])
        if excludeCommitted:
            print("filtering non-committed players")
            players_data = [
                {"player_id": player.get('players'), "player_name":player.get('name')} for player in players_data
                if not player.get("new_team") or str(player.get("new_team")).strip().lower() in ["", "nan"]
            ]
        else:
            players_data = [
                {"player_id": player.get('players'), "player_name":player.get('name')} for player in players_data      
            ]

        tool_context.state["transfer_portal_player_info"] = players_data
        return players_info
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        raise Exception(f"Failed to fetch transfer portal data: {str(e)}")
    
    except ValueError as e:
        print(f"Error parsing API response: {e}")
        raise Exception(f"Invalid API response format: {str(e)}")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise Exception(f"Error filtering transfer portal players: {str(e)}")

def shortlist_players(tool_context: ToolContext, player_ids: List[str]) -> Optional[Dict[Any, Any]]:
    """
    Confirm the shortlisted players that fullfills the given criteria.
    
    Args:
        player_ids (List[str]): List of player IDs
    
    Returns:
        JSON confirmation response from the tool

    """
    schema = "MBB"
    url = f"https://slam-all-python-359065791766.us-central1.run.app/MBB/tp-players/stats?schema={schema}"
    
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "player_ids": player_ids
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        player_stats =  response.json()
        tool_context.state["shortlisted_player_ids"] = player_ids
        # print('player_stats===>',player_stats)
        return player_stats
    
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None

def refine_player_results(
    players: List[Dict[str, Any]],
    filter_criteria: Dict[str, Any],
    sort_by: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Refine a given list of player results with flexible filtering criteria.
    
    Args:
        players (list): List of player dictionaries to filter.
        filter_criteria (dict): Dynamic filtering criteria based on user intent.
        sort_by (str, optional): Sort field and direction ("rank_asc", "bpr_desc").
        limit (int, optional): Maximum number of results to return.

    Returns:
        List of filtered and sorted player dictionaries.
    """
    
    filtered_players = players.copy()
    
    # Apply dynamic filtering based on criteria
    for field, criteria in filter_criteria.items():
        if isinstance(criteria, dict):
            # Range-based filtering
            if "min" in criteria:
                min_val = criteria["min"]
                filtered_players = [
                    player for player in filtered_players 
                    if player.get(field) is not None and _safe_numeric_compare(player.get(field), min_val, ">=")
                ]
            
            if "max" in criteria:
                max_val = criteria["max"]
                filtered_players = [
                    player for player in filtered_players 
                    if player.get(field) is not None and _safe_numeric_compare(player.get(field), max_val, "<=")
                ]
            
            if "exclude" in criteria:
                exclude_vals = criteria["exclude"]
                filtered_players = [
                    player for player in filtered_players 
                    if player.get(field) not in exclude_vals
                ]
                
            if "include" in criteria:
                include_vals = criteria["include"]
                filtered_players = [
                    player for player in filtered_players 
                    if player.get(field) in include_vals
                ]
        else:
            # Direct value matching
            filtered_players = [
                player for player in filtered_players 
                if str(player.get(field, "")).lower() == str(criteria).lower()
            ]
    
    # Apply sorting
    if sort_by:
        field, direction = _parse_sort_criteria(sort_by)
        reverse = direction == "desc"
        try:
            filtered_players = sorted(
                filtered_players,
                key=lambda x: _safe_sort_key(x.get(field)),
                reverse=reverse
            )
        except Exception as e:
            print(f"Sorting error: {e}")
    
    # Apply limit
    if limit:
        filtered_players = filtered_players[:limit]
    
    return filtered_players

def _safe_numeric_compare(value, target, operator):
    """Safely compare numeric values, handling 'nan' and string numbers."""
    if value in ['nan', 'N/A', None, '']:
        return False
    
    try:
        num_value = float(value)
        target_num = float(target)
        
        if operator == ">=":
            return num_value >= target_num
        elif operator == "<=":
            return num_value <= target_num
        elif operator == ">":
            return num_value > target_num
        elif operator == "<":
            return num_value < target_num
        elif operator == "==":
            return num_value == target_num
    except (ValueError, TypeError):
        return False
    
    return False


def _parse_sort_criteria(sort_by):
    """Parse sort criteria like 'rank_asc' or 'bpr_desc'."""
    if "_" in sort_by:
        field, direction = sort_by.rsplit("_", 1)
        direction = direction.lower()
        if direction not in ["asc", "desc"]:
            direction = "asc"
    else:
        field = sort_by
        direction = "asc"
    
    return field, direction


def _safe_sort_key(value):
    """Safe sorting key that handles various data types."""
    if value in ['nan', 'N/A', None, '']:
        return float('inf')  # Put invalid values at the end
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return str(value).lower()


def get_team_requirements(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Mock API tool to fetch team requirements and performance criteria.
    
    Returns comprehensive team performance standards including offensive/defensive
    criteria, position-specific requirements, and skill metrics.
    
    Returns:
        dict: Team requirements and performance criteria data
    """
    print('-------------get_team_requirements---------------')
    
    # Mock API response with comprehensive team requirements
    team_requirements = {
        "team_name": "URI Basketball Team",
        "overall_performance_metrics": {
            "team_performance_standards": {
                "minimum_team_gpa": 2.5,
                "team_free_throw_percentage": 75,
                "max_turnovers_per_game": 15,
                "assist_to_turnover_ratio": 1.2,
                "conference_win_percentage": 65
            }
        },
        "offensive_performance_criteria": {
            "individual_offensive_standards": {
                "guards": {
                    "three_point_percentage": 35,
                    "assists_per_game": 4
                },
                "forwards": {
                    "field_goal_percentage": 50,
                    "rebounds_per_game": 6
                },
                "centers": {
                    "field_goal_percentage": 55,
                    "rebounds_per_game": 8
                },
                "all_players": {
                    "free_throw_percentage": 70
                }
            },
            "team_offensive_benchmarks": {
                "points_per_game": 70,
                "field_goal_percentage": 45,
                "fast_break_points": 12,
                "possession_time": 18
            }
        },
        "defensive_performance_criteria": {
            "individual_defensive_standards": {
                "guards": {
                    "steals_per_game": 2,
                    "opponent_fg_percentage_limit": 40
                },
                "forwards": {
                    "blocks_per_game": 1,
                    "defensive_rebound_percentage": 70
                },
                "centers": {
                    "blocks_per_game": 2,
                    "post_defense_fg_percentage": 45
                },
                "all_players": {
                    "defensive_stance_percentage": 90,
                    "max_fouls_per_game": 4
                }
            },
            "team_defensive_benchmarks": {
                "opponent_points_limit": 65,
                "forced_turnovers": 15,
                "limit_one_shot_percentage": 75,
                "contest_shots_percentage": 85
            }
        },
        "skill_specific_performance_metrics": {
            "position_specific_requirements": {
                "point_guards": {
                    "assists_per_game": 6,
                    "assist_to_turnover_ratio": 2.0,
                    "full_court_pressure_success": 90,
                    "play_execution_accuracy": 95
                },
                "shooting_guards": {
                    "points_per_game": 12,
                    "field_goal_efficiency": 45,
                    "three_pointers_per_game": 2,
                    "defensive_communication_rating": 8
                },
                "forwards": {
                    "double_double_capability": 60,
                    "screen_effectiveness": 85,
                    "fast_break_points": 4
                },
                "centers": {
                    "post_up_efficiency": 60,
                    "rim_protection_percentage": 70,
                    "defensive_communication": 95
                }
            },
            "additional_criteria": {
                "leadership_requirements": "Strong communication and team guidance",
                "work_ethic_standards": "Consistent practice attendance and improvement",
                "character_expectations": "Academic excellence and community involvement",
                "injury_history": "Minimal injury concerns for key positions"
            }
        },
        "recruitment_priorities": {
            "immediate_needs": [
                "Experienced point guard with leadership qualities",
                "Versatile forward with defensive capabilities",
                "Reliable center for rim protection"
            ],
            "depth_requirements": [
                "Bench players with specific skill sets",
                "Development prospects for future seasons"
            ]
        }
    }
    
    # Store the requirements in the tool context state
    tool_context.state["team_requirements"] = team_requirements
    
    return team_requirements

players=[
  {
    "Rank": "1340",
    "name": "Jace Howard",
    "team": "Michigan",
    "new_team": "Fordham",
    "class_": "SR",
    "position": "SF",
    "obpr_predicted": "-0.555123396169723",
    "dbpr_predicted": "0.208566434467989",
    "bpr_predicted": "-0.346556961701734",
    "notes": "nan",
    "recruit_rating_icon": "&#9734 &#9734 &#9734;",
    "dollar_value_string": "nan",
    "height": "80.0",
    "weight": "225.0",
    "possessions": "20",
    "obpr_prev": "-0.655144",
    "dbpr_prev": "0.175151",
    "bpr_prev": "-0.479993",
    "box_obpr_prev": "-0.225428486424348",
    "box_dbpr_prev": "0.0531151750044668",
    "box_bpr_prev": "-0.172313311419882",
    "plus_minus": "1.0",
    "adj_team_off_eff": "78.0470080051323",
    "adj_team_def_eff": "83.0332944797162",
    "adj_team_eff_margin": "-4.98628647458385",
    "role": "5.0",
    "eligible": "True",
    "color_O_pred": "#DFEBF6",
    "color_D_pred": "#FFF9F3",
    "color_Diff_pred": "#EFF5FA",
    "recent": "",
    "color_recent": "#000000",
    "players": "10002386"
  },
  {
    "Rank": "2093",
    "name": "Lazar Grbovic",
    "team": "Eastern Illinois",
    "new_team": "nan",
    "class_": "SR",
    "position": "PF",
    "obpr_predicted": "-1.43849175464737",
    "dbpr_predicted": "-0.0154158523532764",
    "bpr_predicted": "-1.45390760700065",
    "notes": "nan",
    "recruit_rating_icon": "&#9734 &#9734;",
    "dollar_value_string": "nan",
    "height": "80.0",
    "weight": "240.0",
    "possessions": "243",
    "obpr_prev": "-2.18527",
    "dbpr_prev": "0.459066",
    "bpr_prev": "-1.726204",
    "box_obpr_prev": "-1.97740156264635",
    "box_dbpr_prev": "0.14355007467043",
    "box_bpr_prev": "-1.83385148797592",
    "plus_minus": "-23.0",
    "adj_team_off_eff": "85.731407031188",
    "adj_team_def_eff": "100.136239759723",
    "adj_team_eff_margin": "-14.4048327285351",
    "role": "5.0",
    "eligible": "True",
    "color_O_pred": "#AECDE7",
    "color_D_pred": "#FDFEFE",
    "color_Diff_pred": "#BFD7EC",
    "recent": "",
    "color_recent": "#000000",
    "players": "10021846"
  },
  {
    "Rank": "104",
    "name": "Quincy Ballard",
    "team": "Wichita State",
    "new_team": "Mississippi State",
    "class_": "SR",
    "position": "C",
    "obpr_predicted": "1.56117799488453",
    "dbpr_predicted": "1.767391007789",
    "bpr_predicted": "3.32856900267353",
    "notes": "nan",
    "recruit_rating_icon": "&#9734 &#9734 &#9734;",
    "dollar_value_string": "nan",
    "height": "83.0",
    "weight": "251.0",
    "possessions": "1545",
    "obpr_prev": "2.15816",
    "dbpr_prev": "1.71853",
    "bpr_prev": "3.87669",
    "box_obpr_prev": "1.97286505921641",
    "box_dbpr_prev": "1.36564634523557",
    "box_bpr_prev": "3.33851140445198",
    "plus_minus": "69.0",
    "adj_team_off_eff": "109.199647812401",
    "adj_team_def_eff": "96.9656405895482",
    "adj_team_eff_margin": "12.2340072228525",
    "role": "3.15056382458105",
    "eligible": "True",
    "color_O_pred": "#FFE0BA",
    "color_D_pred": "#FFD299",
    "color_Diff_pred": "#FFD095",
    "recent": "",
    "color_recent": "#000000",
    "players": "10022583"
  },
]