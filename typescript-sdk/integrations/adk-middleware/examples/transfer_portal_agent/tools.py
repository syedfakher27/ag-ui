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
    
    This tool allows natural language to SQL conversion for querying the MBB.tp_player_all_stats table.
    If the query has errors, the agent will attempt to fix them and retry.
    
    Args:
        sql_query (str): SQL query to execute against the MBB.tp_player_all_stats table in Spanner database
        
    Table Schema (MBB.tp_player_all_stats):
        players: Unique player identifier  
        Rank: Transfer ranking based on a 5-star system  
        name: Player’s full name  
        team: Current team affiliation  
        new_team: New team affiliation (for transfers)  
        class: Player’s class year (e.g., Freshman, Senior)  
        position: Playing position (e.g., G, F, C) 
        ------------Advance Stats Matrices-------------- 
        obpr_predicted: Projected Offensive BPR for upcoming season  
        dbpr_predicted: Projected Defensive BPR for upcoming season  
        bpr_predicted: Projected overall BPR (OBPR + DBPR) for upcoming season  
        notes: Additional notes or remarks  
        recruit_rating_icon: High school recruit rating indicator  
        dollar_value_string: Estimated dollar value representation  
        height: Player’s height  
        weight: Player’s weight  
        possessions: Number of possessions played in most recent season  
        obpr_prev: Previous season’s Offensive BPR  
        dbpr_prev: Previous season’s Defensive BPR  
        bpr_prev: Previous season’s overall BPR  
        box_obpr_prev: Box-score based Offensive BPR (previous season)  
        box_dbpr_prev: Box-score based Defensive BPR (previous season)  
        box_bpr_prev: Box-score based overall BPR (previous season)  
        plus_minus: Plus-minus value (points differential while on court)  
        adj_team_off_eff: Adjusted team offensive efficiency (points per 100 possessions)  
        adj_team_def_eff: Adjusted team defensive efficiency (points allowed per 100 possessions)  
        adj_team_eff_margin: Adjusted efficiency margin (offensive – defensive)  
        role: Offensive role estimate (1 = creator, 5 = receiver)  
        eligible: Player’s eligibility status  
        recent: Recent performance indicator 
        ------------Core Stats Matrices--------------  
        G: Number of games played by the player  
        MPG: Minutes Per Game (average minutes played per game)  
        PPG: Points Per Game (average points scored per game)  
        FGPct: Field Goal Percentage (two-point and three-point combined), expressed as a number with one decimal (e.g., 49.6 = 49.6%)  
        TwoFGPct: Two-Point Field Goal Percentage (percentage of made 2-pointers)  
        ThreeFGPct: Three-Point Field Goal Percentage (percentage of made 3-pointers)  
        eFGPct: Effective Field Goal Percentage — adjusted FG% that accounts for 3-pointers being worth more  
        FTPct: Free Throw Percentage  
        RPG: Rebounds Per Game (average total rebounds per game)  
        APG: Assists Per Game (average assists per game)  
        SPG: Steals Per Game (average steals per game)  
        BPG: Blocks Per Game (average blocks per game)  
        TOPG: Turnovers Per Game (average turnovers per game)  
        FPG: Fouls Per Game (average personal fouls per game)  
        Eff: Player Efficiency Rating (a composite metric combining various stats into one number)
    
    Note: Always use the full table name `MBB`.`tp_player_all_stats` in your SQL queries.
    
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