from typing import List, Optional, Dict, Any
from google.adk.tools import ToolContext
from urllib.parse import quote
import requests
from google.cloud import spanner
import re
import traceback
import os


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


def text2sql_query_savant_mlb(
    tool_context: ToolContext,
    sql_query: str
):
    """
    Execute a SQL query on the Spanner database to retrieve baseball savant MLB data.
    
    This tool allows natural language to SQL conversion for querying the MBB.savant_mlb table.
    If the query has errors, the agent will attempt to fix them and retry.
    
    Args:
        sql_query (str): SQL query to execute against the MBB.savant_mlb table in Spanner database
        
    Table Schema (MBB.savant_mlb):
        Primary Key: player_id (INT64) - Unique identifier for the player
        
        Core Columns:
        - pitches: INT64 - Total number of pitches
        - player_id: INT64 NOT NULL - Unique identifier for the player (Primary Key)
        - player_name: STRING(255) - Full name of the baseball player
        - total_pitches: INT64 - Total pitches thrown or faced
        - hits: INT64 - Total hits
        - abs: INT64 - At-bats
        - whiffs: INT64 - Swings and misses
        - swings: INT64 - Total swings
        - takes: INT64 - Pitches taken (not swung at)
        - pa: INT64 - Plate appearances
        - bip: INT64 - Balls in play
        - singles: INT64 - Single hits
        - doubles: INT64 - Double hits
        - triples: INT64 - Triple hits
        - hrs: INT64 - Home runs
        - so: INT64 - Strikeouts
        - bb: INT64 - Walks (base on balls)
        - barrels_total: INT64 - Total barrels (optimal contact metric)
        
        Percentage/Rate Statistics:
        - pitch_percent: FLOAT64 - Pitch usage percentage
        - ba: FLOAT64 - Batting average
        - iso: FLOAT64 - Isolated power (slugging - batting average)
        - babip: FLOAT64 - Batting average on balls in play
        - slg: FLOAT64 - Slugging percentage
        - woba: FLOAT64 - Weighted on-base average
        - xwoba: FLOAT64 - Expected weighted on-base average
        - xba: FLOAT64 - Expected batting average
        - k_percent: FLOAT64 - Strikeout percentage
        - bb_percent: FLOAT64 - Walk percentage
        - hardhit_percent: FLOAT64 - Hard hit percentage
        - barrels_per_bbe_percent: FLOAT64 - Barrels per batted ball event percentage
        - barrels_per_pa_percent: FLOAT64 - Barrels per plate appearance percentage
        - obp: FLOAT64 - On-base percentage
        - xobp: FLOAT64 - Expected on-base percentage
        - xslg: FLOAT64 - Expected slugging percentage
        - swing_miss_percent: FLOAT64 - Swing and miss percentage
        
        Physical/Kinematic Metrics:
        - launch_speed: FLOAT64 - Average exit velocity
        - launch_angle: FLOAT64 - Average launch angle
        - spin_rate: INT64 - Pitch spin rate (RPM)
        - velocity: FLOAT64 - Pitch velocity
        - effective_speed: FLOAT64 - Effective velocity accounting for extension
        - eff_min_vel: FLOAT64 - Minimum effective velocity
        - release_extension: FLOAT64 - Release point extension
        - release_pos_z: FLOAT64 - Vertical release position
        - release_pos_x: FLOAT64 - Horizontal release position
        - plate_x: FLOAT64 - Horizontal location at home plate
        - plate_z: FLOAT64 - Vertical location at home plate
        - bat_speed: FLOAT64 - Bat speed at contact
        - swing_length: FLOAT64 - Length of swing path
        - arm_angle: FLOAT64 - Arm angle at release
        - attack_angle: FLOAT64 - Bat's attack angle
        - attack_direction: FLOAT64 - Direction of bat's attack
        - swing_path_tilt: FLOAT64 - Tilt of swing path
        - rate_ideal_attack_angle: FLOAT64 - Rate of ideal attack angles
        
        Advanced Metrics:
        - api_break_z_with_gravity: FLOAT64 - Vertical break including gravity
        - api_break_z_induced: FLOAT64 - Induced vertical break
        - api_break_x_arm: FLOAT64 - Horizontal break from arm side
        - api_break_x_batter_in: FLOAT64 - Horizontal break toward batter
        - hyper_speed: FLOAT64 - Hyper speed metric
        - bbdist: FLOAT64 - Batted ball distance
        - batter_run_value_per_100: FLOAT64 - Batter run value per 100 pitches
        - pitcher_run_value_per_100: FLOAT64 - Pitcher run value per 100 pitches
        - pitcher_run_exp: FLOAT64 - Pitcher run expectancy
        - run_exp: FLOAT64 - Run expectancy
        - xbadiff: FLOAT64 - Difference between actual and expected batting average
        - xobpdiff: FLOAT64 - Difference between actual and expected OBP
        - xslgdiff: FLOAT64 - Difference between actual and expected SLG
        - wobadiff: FLOAT64 - Difference between actual and expected wOBA
        
        Position-specific Metrics:
        - pos3_int_start_distance: FLOAT64 - First baseman starting distance
        - pos4_int_start_distance: FLOAT64 - Second baseman starting distance
        - pos5_int_start_distance: FLOAT64 - Third baseman starting distance
        - pos6_int_start_distance: FLOAT64 - Shortstop starting distance
        - pos7_int_start_distance: FLOAT64 - Left fielder starting distance
        - pos8_int_start_distance: FLOAT64 - Center fielder starting distance
        - pos9_int_start_distance: FLOAT64 - Right fielder starting distance
        
        Intercept Metrics:
        - intercept_ball_minus_batter_pos_x_inches: FLOAT64 - X-axis intercept difference
        - intercept_ball_minus_batter_pos_y_inches: FLOAT64 - Y-axis intercept difference
    
    Note: Always use the full table name `MBB`.`savant_mlb` in your SQL queries.
    
    Returns:
        dict: Query results with baseball savant MLB data
        
    Raises:
        Exception: If database connection fails or query cannot be executed after retry
    """
    print(f'-------------text2sql_query_savant_mlb---------------')
    print(f'Executing SQL Query: {sql_query}')
    
    # Initialize Spanner client
    instance_id = os.environ.get('SPANNER_INSTANCE_ID','slam-spanner')
    database_id = os.environ.get('SPANNER_DATABASE_ID','slam-db')
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT','slamsportsai')
    
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
                tool_context.state["tool_context"] = sql_query
                
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
                    "suggestion": "Please check the SQL syntax and table schema. The table name is `MBB`.`savant_mlb` and common issues include: incorrect column names, missing WHERE clauses, or syntax errors."
                }
            
            # For certain errors, suggest fixes
            if "not found" in error_msg.lower() or "invalid" in error_msg.lower():
                print(f"Query error detected. Agent should fix and retry. Error: {error_msg}")
                # Let the agent handle the error and retry with a corrected query
                return {
                    "success": False,
                    "error": error_msg,
                    "query": sql_query,
                    "retry_suggestion": f"SQL error encountered: {error_msg}. Please fix the query and try again. Remember to use `MBB`.`savant_mlb` as the table name.",
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


# if __name__=="__main__":
#     result = text2sql_query_transfer_portal("SELECT player_name, bpr_predicted FROM MBB.tp_player_view WHERE position = 'PG' AND (new_team IS NULL OR new_team = '' OR new_team = 'nan') ORDER BY bpr_predicted DESC LIMIT 5")
#     print('result==>',result)