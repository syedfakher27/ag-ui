from typing import List, Optional, Dict, Any
from google.adk.tools import ToolContext
from urllib.parse import quote
import requests
from google.cloud import spanner
import re
import traceback
import os

def text2sql_query_player_advance_stats(
    tool_context: ToolContext,
    sql_query: str
):
    """
    Execute a SQL query on the Spanner database to retrieve player advance stats data.
    
    This tool allows natural language to SQL conversion for querying the MBB.player_advance_stats table.
    If the query has errors, the agent will attempt to fix them and retry.
    
    Args:
        sql_query (str): SQL query to execute against the MBB.player_advance_stats table in Spanner database
        
    Table Schema (MBB.player_advance_stats):
        Primary Key: player_id (STRING) - Unique identifier for the player
        All columns are of type STRING(MAX) — treat all values as strings unless explicitly converted.
        
        - university: Full name of the university or college the player represents
        - team_name: Short name of the team (often without 'University' or 'College')
        - player_name: Full name of the basketball player
        - position: Player's primary position (e.g., F = Forward, G = Guard, C = Center)
        - height: Player's height in feet and inches, formatted as X'Y" (feet'inches")
        - weight: Player's weight in pounds, including "lbs" unit
        - player_id: Unique identifier for the player (Primary Key)
        - team: Team name associated with the player; may be identical to team_name
        - class: Academic or eligibility class of the player (e.g., FR = Freshman, SO = Sophomore, JR = Junior, SR = Senior)
        - poss: Total number of possessions the player has participated in (numeric value stored as string)
        - value_three_pct: Metric representing the player's value or efficiency from three-point shooting (as a decimal string)
        - value_two_pct: Metric representing the player's value from two-point shooting (as a decimal string)
        - value_ft_pct: Metric representing the player's value from free throw shooting (as a decimal string)
        - value_scoring: Composite scoring efficiency value (higher is better)
        - value_assist_rate: Value metric related to assists per possession or assist frequency
        - value_TO: Turnover-related value (can be negative; lower or negative values indicate more turnovers)
        - value_playmaking: Overall playmaking impact score (can be negative if poor decision-making)
        - value_oreb_pct: Offensive rebound percentage value (share of available offensive rebounds captured)
        - value_dreb_pct: Defensive rebound percentage value (share of available defensive rebounds captured)
        - value_reb_pct: Total rebound percentage value (combined offensive and defensive)
        - value_blk_pct: Block percentage value (share of opponent two-point attempts blocked while on court)
        - value_STL: Steals value metric (frequency or impact of steals)
        - value_PF: Personal fouls value (higher may indicate foul trouble or aggressive play)
        - value_D: Overall defensive impact value (composite metric)
    
    Note: Always use the full table name `MBB`.`player_advance_stats` in your SQL queries.
    
    Returns:
        dict: Query results with player advance stats data
        
    Raises:
        Exception: If database connection fails or query cannot be executed after retry
    """
    print(f'-------------text2sql_query_player_advance_stats---------------')
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
                    "suggestion": "Please check the SQL syntax and table schema. The table name is `MBB`.`player_advance_stats` and common issues include: incorrect column names, missing WHERE clauses, or syntax errors."
                }
            
            # For certain errors, suggest fixes
            if "not found" in error_msg.lower() or "invalid" in error_msg.lower():
                print(f"Query error detected. Agent should fix and retry. Error: {error_msg}")
                # Let the agent handle the error and retry with a corrected query
                return {
                    "success": False,
                    "error": error_msg,
                    "query": sql_query,
                    "retry_suggestion": f"SQL error encountered: {error_msg}. Please fix the query and try again. Remember to use `MBB`.`player_advance_stats` as the table name.",
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

def text2sql_query_core_stats(
    tool_context: ToolContext,
    sql_query: str
):
    """
    Execute a SQL query on the Spanner database to retrieve player core stats data.
    
    This tool allows natural language to SQL conversion for querying the MBB.player_core_stats_view table.
    If the query has errors, the agent will attempt to fix them and retry.
    
    Args:
        sql_query (str): SQL query to execute against the MBB.player_core_stats_view table in Spanner database
        
    Table Schema (MBB.player_core_stats_view):
        All columns are of type STRING — treat all values as strings unless explicitly converted.
        Columns description:

        team_name: STRING
        - Description: Full name of the team.
        - Example: "Rhode Island"

        Rank: STRING
        - Description: Player ranking
        - Example: "3"

        Player: STRING
        - Description: Full name of the player; serves as a primary identifier in this view.
        - Example: "Bradyn Hubbard"

        G: STRING
        - Description: Number of games played by the player.
        - Example: "31"

        MPG: STRING
        - Description: Minutes Per Game (average minutes played per game).
        - Example: "23.2"

        PPG: STRING
        - Description: Points Per Game (average points scored per game).
        - Example: "10.2"

        FGPct: STRING
        - Description: Field Goal Percentage (two-point and three-point combined), expressed as a number with one decimal (e.g., "49.6" = 49.6%).
        - Example: "49.6"

        TwoFGPct: STRING
        - Description: Two-Point Field Goal Percentage (percentage of made 2-pointers).
        - Example: "51.3"

        ThreeFGPct: STRING
        - Description: Three-Point Field Goal Percentage (percentage of made 3-pointers).
        - Example: "42.6"

        eFGPct: STRING
        - Description: Effective Field Goal Percentage — adjusted FG% that accounts for 3-pointers being worth more.
        - Example: "53.8"

        FTPct: STRING
        - Description: Free Throw Percentage.
        - Example: "84.0"

        RPG: STRING
        - Description: Rebounds Per Game (average total rebounds per game).
        - Example: "5.7"

        APG: STRING
        - Description: Assists Per Game (average assists per game).
        - Example: "0.8"

        SPG: STRING
        - Description: Steals Per Game (average steals per game).
        - Example: "1.4"

        BPG: STRING
        - Description: Blocks Per Game (average blocks per game).
        - Example: "0.2"

        TOPG: STRING
        - Description: Turnovers Per Game (average turnovers per game).
        - Example: "1.5"

        FPG: STRING
        - Description: Fouls Per Game (average personal fouls per game).
        - Example: "0.0"

        Eff: STRING
        - Description: Player Efficiency Rating (a composite metric combining various stats into one number).
        - Example: "8.1"
    
    Note: Always use the full table name `MBB`.`player_core_stats_view` in your SQL queries.
    
    Returns:
        dict: Query results with player core stats data
        
    Raises:
        Exception: If database connection fails or query cannot be executed after retry
    """
    print(f'-------------text2sql_query_core_stats---------------')
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
                    "suggestion": "Please check the SQL syntax and table schema. The table name is `MBB`.`player_core_stats_view` and common issues include: incorrect column names, missing WHERE clauses, or syntax errors."
                }
            
            # For certain errors, suggest fixes
            if "not found" in error_msg.lower() or "invalid" in error_msg.lower():
                print(f"Query error detected. Agent should fix and retry. Error: {error_msg}")
                # Let the agent handle the error and retry with a corrected query
                return {
                    "success": False,
                    "error": error_msg,
                    "query": sql_query,
                    "retry_suggestion": f"SQL error encountered: {error_msg}. Please fix the query and try again. Remember to use `MBB`.`player_core_stats_view` as the table name.",
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