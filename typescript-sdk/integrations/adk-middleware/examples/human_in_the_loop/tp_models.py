from typing import Dict, List, Literal, TypedDict
import random

# Type definitions matching TypeScript interfaces
Position = Literal["PG", "SG", "SF", "PF", "C"]
StyleOfPlay = Literal["Transition offense", "Half-court offense", "Defense-first", "Balanced"]
DevelopmentReadiness = Literal["Immediate impact", "Multi-year potential", "Project player"]

class AvailabilityStatus(TypedDict):
    stillAvailable: bool
    committed: bool
    draftBound: bool

class TransferPortalFilters(TypedDict):
    positionGap: Position
    styleOfPlay: StyleOfPlay
    developmentReadiness: DevelopmentReadiness
    minutesPerGame: int
    efficiencyRating: int
    reboundBlockAssist: int
    availability: AvailabilityStatus

class BasketballPlayer(TypedDict):
    id: int
    name: str
    position: Position
    previous_team: str
    years_remaining: int
    height: str
    weight: int
    ppg: float
    rpg: float
    apg: float
    minutes_per_game: float
    efficiency_rating: float
    rebound_block_assist_percentage: float
    style_of_play: StyleOfPlay
    development_readiness: DevelopmentReadiness
    availability_status: str
    nil_value: str
    hometown: str
    highlights: List[str]
    video_link: str

def generate_mock_players() -> List[BasketballPlayer]:
    """Generate mock basketball players data"""
    
    players = [
        {
            "id": 1,
            "name": "Marcus Thompson",
            "position": "PG",
            "previous_team": "Duke University",
            "years_remaining": 2,
            "height": "6'2\"",
            "weight": 185,
            "ppg": 15.3,
            "rpg": 4.2,
            "apg": 7.8,
            "minutes_per_game": 32.1,
            "efficiency_rating": 78.5,
            "rebound_block_assist_percentage": 65.2,
            "style_of_play": "Transition offense",
            "development_readiness": "Immediate impact",
            "availability_status": "Still available",
            "nil_value": "High",
            "hometown": "Atlanta, GA",
            "highlights": ["Elite court vision", "Strong leadership", "Clutch performer"],
            "video_link": "https://example.com/marcus-highlights"
        },
        {
            "id": 2,
            "name": "Jaylen Rodriguez",
            "position": "SG",
            "previous_team": "Villanova",
            "years_remaining": 1,
            "height": "6'4\"",
            "weight": 205,
            "ppg": 18.7,
            "rpg": 5.1,
            "apg": 3.4,
            "minutes_per_game": 29.8,
            "efficiency_rating": 82.3,
            "rebound_block_assist_percentage": 58.7,
            "style_of_play": "Half-court offense",
            "development_readiness": "Immediate impact",
            "availability_status": "Still available",
            "nil_value": "Very High",
            "hometown": "Chicago, IL",
            "highlights": ["Excellent shooter", "Defensive versatility", "Experience in big games"],
            "video_link": "https://example.com/jaylen-highlights"
        },
        {
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
        },
        {
            "id": 4,
            "name": "Connor Mitchell",
            "position": "PF",
            "previous_team": "URI",
            "years_remaining": 2,
            "height": "6'9\"",
            "weight": 235,
            "ppg": 10.5,
            "rpg": 9.4,
            "apg": 1.8,
            "minutes_per_game": 28.3,
            "efficiency_rating": 68.9,
            "rebound_block_assist_percentage": 78.1,
            "style_of_play": "Balanced",
            "development_readiness": "Multi-year potential",
            "availability_status": "Still available",
            "nil_value": "Undervalued",
            "hometown": "Portland, OR",
            "highlights": ["Multi-year fit", "High rebound rate", "Solid fundamentals"],
            "video_link": "https://example.com/connor-highlights"
        },
        {
            "id": 5,
            "name": "Zion Parker",
            "position": "C",
            "previous_team": "Arizona",
            "years_remaining": 1,
            "height": "6'11\"",
            "weight": 250,
            "ppg": 14.2,
            "rpg": 11.3,
            "apg": 2.1,
            "minutes_per_game": 26.7,
            "efficiency_rating": 75.6,
            "rebound_block_assist_percentage": 85.3,
            "style_of_play": "Defense-first",
            "development_readiness": "Immediate impact",
            "availability_status": "Committed",
            "nil_value": "High",
            "hometown": "Los Angeles, CA",
            "highlights": ["Elite rim protector", "Dominant rebounder", "NBA-ready body"],
            "video_link": "https://example.com/zion-highlights"
        },
        {
            "id": 6,
            "name": "Tyler Brooks",
            "position": "PG",
            "previous_team": "Gonzaga",
            "years_remaining": 2,
            "height": "6'0\"",
            "weight": 175,
            "ppg": 8.9,
            "rpg": 2.8,
            "apg": 6.2,
            "minutes_per_game": 22.4,
            "efficiency_rating": 64.7,
            "rebound_block_assist_percentage": 45.8,
            "style_of_play": "Transition offense",
            "development_readiness": "Project player",
            "availability_status": "Still available",
            "nil_value": "Moderate",
            "hometown": "Seattle, WA",
            "highlights": ["Great potential", "Needs development", "High upside"],
            "video_link": "https://example.com/tyler-highlights"
        },
        {
            "id": 7,
            "name": "Anthony Davis Jr.",
            "position": "PF",
            "previous_team": "Kentucky",
            "years_remaining": 1,
            "height": "6'10\"",
            "weight": 240,
            "ppg": 16.8,
            "rpg": 8.9,
            "apg": 2.4,
            "minutes_per_game": 31.2,
            "efficiency_rating": 79.4,
            "rebound_block_assist_percentage": 81.6,
            "style_of_play": "Balanced",
            "development_readiness": "Immediate impact",
            "availability_status": "Draft-bound",
            "nil_value": "Very High",
            "hometown": "New Orleans, LA",
            "highlights": ["NBA prospect", "Versatile scorer", "Strong athleticism"],
            "video_link": "https://example.com/anthony-highlights"
        },
        {
            "id": 8,
            "name": "Jake Morrison",
            "position": "SG",
            "previous_team": "Butler",
            "years_remaining": 3,
            "height": "6'5\"",
            "weight": 195,
            "ppg": 11.7,
            "rpg": 4.3,
            "apg": 3.1,
            "minutes_per_game": 24.8,
            "efficiency_rating": 69.3,
            "rebound_block_assist_percentage": 52.4,
            "style_of_play": "Half-court offense",
            "development_readiness": "Multi-year potential",
            "availability_status": "Still available",
            "nil_value": "Moderate",
            "hometown": "Indianapolis, IN",
            "highlights": ["Consistent shooter", "Team player", "Good fundamentals"],
            "video_link": "https://example.com/jake-highlights"
        }
    ]
    
    return players