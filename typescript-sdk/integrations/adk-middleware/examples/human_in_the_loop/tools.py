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


# if __name__=="__main__":
#     result = text2sql_query_transfer_portal("SELECT player_name, bpr_predicted FROM MBB.tp_player_view WHERE position = 'PG' AND (new_team IS NULL OR new_team = '' OR new_team = 'nan') ORDER BY bpr_predicted DESC LIMIT 5")
#     print('result==>',result)