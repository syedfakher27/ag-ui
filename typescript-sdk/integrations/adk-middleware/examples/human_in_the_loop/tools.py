from typing import List, Optional, Dict, Any
from google.adk.tools import ToolContext
from urllib.parse import quote
import requests
from google.cloud import spanner
import re
import traceback
import os

def text2sql_query_transfer_portal(
    tool_context: ToolContext,
    sql_query: str
):
    """
    Execute a SQL query on the Spanner database to retrieve transfer portal player data.
    
    This tool allows natural language to SQL conversion for querying the MBB.tp_player_view table.
    If the query has errors, the agent will attempt to fix them and retry.
    
    Args:
        sql_query (str): SQL query to execute against the MBB.tp_player_view table in Spanner database
        
    Table Schema (MBB.tp_player_view):
        - player_id: Unique identifier for each player
        - player_rank: Player's ranking position  
        - player_name: Full name of the player
        - team: Current team affiliation
        - new_team: New team affiliation (for transfers)
        - player_class: Player's academic class (FR, SO, JR, SR)
        - position: Player's position (PG, SG, SF, PF, C)
        - offensive_bpr: Projected offensive BPR rating (higher is better)
        - defensive_bpr: Projected defensive BPR rating (higher is better)
        - bpr_predicted: Projected overall BPR rating (higher is better)
        - notes: Additional notes about the player
        - dollar_value_string: Monetary value assessment
        - height: Player's height in inches
        - weight: Player's weight in pounds
        - possessions: Number of possessions played in recent season
        - obpr_prev: Previous offensive BPR rating
        - dbpr_prev: Previous defensive BPR rating
        - bpr_prev: Previous overall BPR rating
        - box_obpr_prev: Previous box score offensive BPR
        - box_dbpr_prev: Previous box score defensive BPR
        - box_bpr_prev: Previous box score overall BPR
        - plus_minus: Plus/minus statistic
        - adj_team_off_eff: Adjusted team offensive efficiency
        - adj_team_def_eff: Adjusted team defensive efficiency
        - adj_team_eff_margin: Adjusted team efficiency margin
        - role: Player role classification
        - eligible: Eligibility status
        - three_point_percent: Three-point shooting percentage
        - two_point_percent: Two-point shooting percentage
        - free_throw_percent: Free throw shooting percentage
        - assist_rate: Assist rate statistic
        - turnover_percent: Turnover percentage
        - playmaking_score: Playmaking ability score
        - offensive_rebound_percent: Offensive rebounding percentage
        - defensive_rebound_percentage: Defensive rebounding percentage
        - rebound_percent: Overall rebounding percentage
        - block_percent: Block percentage
        - steal_percent: Steal percentage
        - personal_foul_percent: Personal foul percentage
        - defensive_value: Defensive value metric
    
    Note: Always use the full table name `MBB`.`tp_player_view` in your SQL queries.
    
    Returns:
        dict: Query results with player data
        
    Raises:
        Exception: If database connection fails or query cannot be executed after retry
    """
    print(f'-------------text2sql_query_transfer_portal---------------')
    print(f'Executing SQL Query: {sql_query}')
    
    # Initialize Spanner client
    instance_id = os.environ.get('SPANNER_INSTANCE_ID','slam-spanner')
    database_id = os.environ.get('SPANNER_DATABASE_ID','slam-db')
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT','slamsportsai')  # Replace with your actual project ID
    
    max_retries = 3
    current_retry = 0
    
    while current_retry < max_retries:
        try:
            # Create Spanner client
            spanner_client = spanner.Client(project=project_id)
            instance = spanner_client.instance(instance_id)
            database = instance.database(database_id)
            
            # Modify query to ensure max 50 records to prevent model overflow
            modified_query = sql_query
            if "LIMIT" not in sql_query.upper():
                modified_query = f"{sql_query} LIMIT 50"
            else:
                # Extract existing limit and ensure it's not more than 50
                import re
                limit_match = re.search(r'LIMIT\s+(\d+)', sql_query, re.IGNORECASE)
                if limit_match:
                    existing_limit = int(limit_match.group(1))
                    if existing_limit > 50:
                        modified_query = re.sub(r'LIMIT\s+\d+', 'LIMIT 50', sql_query, flags=re.IGNORECASE)
            
            print(f"Modified Query (max 50 records): {modified_query}")
            
            # Execute the query
            with database.snapshot() as snapshot:
                results = snapshot.execute_sql(modified_query)
                
                # Convert results to list of dictionaries
                players_data = []
                columns = None
                
                try:
                    # Process results row by row to avoid snapshot reuse issues
                    first_row = True
                    for row in results:
                        if first_row:
                            # Get column names from the first row's metadata
                            if hasattr(results, '_metadata') and results._metadata and hasattr(results._metadata, 'row_type'):
                                columns = [field.name for field in results.fields]
                            else:
                                raise Exception("Query results do not contain proper metadata/schema information.")
                            first_row = False
                        
                        # Process the row
                        player_dict = {}
                        for i, value in enumerate(row):
                            player_dict[columns[i]] = value
                        players_data.append(player_dict)
                    
                    # If no rows were processed but query succeeded
                    if not players_data and columns is None:
                        print("Query executed successfully but returned no records.")
                        return {
                            "success": True,
                            "data": [],
                            "total_records": 0,
                            "query": sql_query,
                            "columns": []
                        }
                        
                except Exception as field_error:
                    # If we still can't process results, there's a deeper issue
                    raise Exception(f"Query executed but failed to process results: {str(field_error)}. This may indicate authentication, permissions, or schema issues.")
                
                print(f"Query executed successfully. Retrieved {len(players_data)} records.")
                
                # Store results in tool context
                # tool_context.state["transfer_portal_player_info"] = [
                #     {"player_id": str(player.get('player_id', '')), "player_name": str(player.get('player_name', ''))} 
                #     for player in players_data
                # ]
                tool_context.state["tool_context"] = sql_query
                # tool_context.state["sql_query_results_count"] = len(players_data)
                
                return {
                    "success": True,
                    "data": players_data,
                    "total_records": len(players_data),
                    "query": sql_query,
                    "columns": columns
                }
                
        except Exception as e:
            traceback.print_exc()
            current_retry += 1
            error_msg = str(e)
            print(f"SQL Query Error (Attempt {current_retry}/{max_retries}): {error_msg}")
            
            if current_retry >= max_retries:
                # After max retries, return error for agent to handle
                return {
                    "success": False,
                    "error": error_msg,
                    "query": sql_query,
                    "suggestion": "Please check the SQL syntax and table schema. The table name is `MBB`.`tp_player_view` and common issues include: incorrect column names, missing WHERE clauses, or syntax errors."
                }
            
            # For certain errors, suggest fixes
            if "not found" in error_msg.lower() or "invalid" in error_msg.lower():
                print(f"Query error detected. Agent should fix and retry. Error: {error_msg}")
                # Let the agent handle the error and retry with a corrected query
                return {
                    "success": False,
                    "error": error_msg,
                    "query": sql_query,
                    "retry_suggestion": f"SQL error encountered: {error_msg}. Please fix the query and try again. Remember to use `MBB`.`tp_player_view` as the table name.",
                    "can_retry": True,
                    "attempts_remaining": max_retries - current_retry
                }
            
            # For other errors, continue retrying with same query
            continue
    
    return {
        "success": False,
        "error": f"Query failed after {max_retries} attempts",
        "query": sql_query
    }

def shortlist_players(tool_context: ToolContext, player_names: List[str] = [], player_ids: List[str] = []) -> Optional[Dict[Any, Any]]:
    """
    Confirm the shortlisted players that fullfills the given criteria Or get the player stats using provided player names. Do not use the player_ids and player_names both
    
    Args:
        player_names (List[str]) Optional: List of player Names
        player_ids (List[str]) Optional: List of player IDs
    
    Returns:
        Player Stats response from the tool

    """
    schema = "MBB"
    url = f"https://slam-all-python-359065791766.us-central1.run.app/MBB/tp-players/stats?schema={schema}"
    
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "player_ids": player_ids,
        "player_names": player_names,
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


if __name__=="__main__":
    result = text2sql_query_transfer_portal("SELECT player_name, bpr_predicted FROM MBB.tp_player_view WHERE position = 'PG' AND (new_team IS NULL OR new_team = '' OR new_team = 'nan') ORDER BY bpr_predicted DESC LIMIT 5")
    print('result==>',result)