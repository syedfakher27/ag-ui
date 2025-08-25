from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any


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