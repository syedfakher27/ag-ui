#!/usr/bin/env python3
"""
Single File Test for Player Data Extraction Agent

This script tests the extraction agent with a single file for focused debugging.
"""

import asyncio
import logging
import json
from typing import AsyncGenerator, List, Dict, Any

from adk_middleware import ADKAgent, AgentRegistry
from ag_ui.core import RunAgentInput, BaseEvent, Message, UserMessage, Context
from agent import player_data_extraction_agent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_event(event: BaseEvent):
    """Handle and display AG-UI events for data extraction."""
    event_type = event.type.value if hasattr(event.type, 'value') else str(event.type)
    
    if event_type == "RUN_STARTED":
        print("📊 Player Data Extraction Started")
    elif event_type == "RUN_FINISHED":
        print("✅ Extraction Complete")
    elif event_type == "RUN_ERROR":
        print(f"❌ Extraction Error: {event.message}")
    elif event_type == "TEXT_MESSAGE_START":
        print("🔍 Processing: ", end="", flush=True)
    elif event_type == "TEXT_MESSAGE_CONTENT":
        print(event.delta, end="", flush=True)
    elif event_type == "TEXT_MESSAGE_END":
        print()  # New line after message
    elif event_type == "TOOL_CALL_START":
        tool_name = getattr(event, 'tool_name', 'Unknown Tool')
        print(f"🔧 Using {tool_name}...")
    elif event_type == "TOOL_CALL_END":
        print(f"✓ Tool execution completed")
    else:
        print(f"📋 Event: {event_type}")


def validate_extraction_result(content: str) -> Dict[str, Any]:
    """Validate and parse extraction results."""
    try:
        # Clean common markdown formatting
        cleaned_content = content.strip()
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]
        
        # Parse JSON
        parsed_data = json.loads(cleaned_content)
        
        if not isinstance(parsed_data, list):
            return {
                "valid": False,
                "error": "Response is not a JSON array",
                "data": None
            }
        
        # Validate structure
        issues = []
        for i, player_entry in enumerate(parsed_data):
            if not isinstance(player_entry, dict):
                issues.append(f"Player entry {i} is not a dictionary")
                continue
            
            if "player" not in player_entry:
                issues.append(f"Player entry {i} missing 'player' field")
            
            if "data" not in player_entry:
                issues.append(f"Player entry {i} missing 'data' field")
            elif not isinstance(player_entry["data"], dict):
                issues.append(f"Player entry {i} 'data' field is not a dictionary")
        
        return {
            "valid": len(issues) == 0,
            "player_count": len(parsed_data),
            "issues": issues,
            "data": parsed_data,
            "sample_player": parsed_data[0]["player"] if parsed_data else None,
            "sample_fields": list(parsed_data[0]["data"].keys()) if parsed_data and "data" in parsed_data[0] else []
        }
        
    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "error": f"JSON parsing failed: {str(e)}",
            "data": None,
            "raw_content": content
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}",
            "data": None,
            "raw_content": content
        }


async def test_single_file_extraction(gcs_url: str, description: str = ""):
    """Test extraction of basketball statistics from a single file."""
    
    # Register the player data extraction agent
    registry = AgentRegistry.get_instance()
    registry.register_agent("data_extractor", player_data_extraction_agent)
    
    # Create the middleware agent
    agent = ADKAgent(
        user_id="single_test_user",
        app_name="single_file_extraction"
    )
    
    # Create extraction request
    run_input = RunAgentInput(
        thread_id=f"single_test_{hash(gcs_url)}",
        run_id="single_extraction_001",
        messages=[
            UserMessage(
                id="single_extraction_request",
                role="user",
                content=f"""Please extract all player data from this basketball document:

GCS URL: {gcs_url}

{description}

Requirements:
1. Process ALL visible players in the document systematically
2. Extract complete data for each player row
3. Maintain exact player names (including jersey numbers like #7 Harper, #23 Marcus Brown)
4. For images: Use systematic cropping approach to process the table
   - First analyze the full image structure
   - Crop and extract header row
   - Process each data row individually
5. Return valid JSON format with player names and statistics
6. Use null for empty/missing values (not "N/A" or empty strings)
7. Skip summary/total rows

Follow your systematic processing workflow step by step for maximum accuracy."""
            )
        ],
        context=[
            Context(description="extraction_type", value="basketball_statistics"),
            Context(description="source_url", value=gcs_url),
            Context(description="agent_id", value="data_extractor"),
            Context(description="validation_required", value="true"),
            Context(description="test_mode", value="single_file")
        ],
        state={
            "data_extraction": {
                "processed_files": [],
                "current_focus": "Single File Player Statistics Extraction",
                "debug_mode": True
            }
        },
        tools=[],
        forwarded_props={}
    )
    
    print(f"📊 Starting Single File Player Data Extraction")
    print(f"📁 Source File: {gcs_url}")
    if description:
        print(f"📝 Description: {description}")
    print("=" * 80)
    
    extracted_content = ""
    
    try:
        async for event in agent.run(run_input):
            handle_event(event)
            
            # Capture the final response content
            if hasattr(event, 'delta') and event.delta:
                extracted_content += event.delta
                
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        return {"success": False, "error": str(e)}
    finally:
        await agent.close()
    
    print(f"\n📝 RAW EXTRACTED CONTENT:")
    print("=" * 50)
    print(extracted_content[:1000] + "..." if len(extracted_content) > 1000 else extracted_content)
    
    # Validate results
    if extracted_content:
        validation_result = validate_extraction_result(extracted_content)
        
        print(f"\n📊 EXTRACTION RESULTS")
        print("=" * 50)
        
        if validation_result["valid"]:
            print(f"✅ Status: SUCCESS")
            print(f"👥 Players Extracted: {validation_result['player_count']}")
            
            if validation_result["sample_player"]:
                print(f"📋 Sample Player: {validation_result['sample_player']}")
            
            if validation_result["sample_fields"]:
                print(f"📊 Sample Fields: {validation_result['sample_fields'][:8]}")
                if len(validation_result['sample_fields']) > 8:
                    print(f"    ... and {len(validation_result['sample_fields']) - 8} more fields")
            
            # Print detailed player data for verification
            print(f"\n📋 DETAILED PLAYER DATA:")
            print("-" * 50)
            for i, player_data in enumerate(validation_result["data"][:5]):  # Show first 5 players
                print(f"Player {i+1}: {player_data['player']}")
                if isinstance(player_data.get('data'), dict):
                    for key, value in list(player_data['data'].items())[:10]:  # Show first 10 fields
                        print(f"  {key}: {value}")
                if i < len(validation_result["data"]) - 1:
                    print()
            
            if len(validation_result["data"]) > 5:
                print(f"... and {len(validation_result['data']) - 5} more players")
            
            return {
                "success": True,
                "player_count": validation_result["player_count"],
                "data": validation_result["data"],
                "validation": validation_result
            }
        else:
            print(f"❌ Status: VALIDATION FAILED")
            print(f"🔍 Error: {validation_result.get('error', 'Unknown validation error')}")
            if validation_result.get("issues"):
                print(f"📋 Issues: {validation_result['issues']}")
            
            # Show raw content for debugging
            if validation_result.get("raw_content"):
                print(f"\n📝 RAW CONTENT FOR DEBUGGING:")
                print("-" * 50)
                print(validation_result["raw_content"][:2000])
            
            return {
                "success": False,
                "error": validation_result.get("error", "Validation failed"),
                "raw_content": extracted_content,
                "validation": validation_result
            }
    else:
        print(f"❌ No content extracted")
        return {"success": False, "error": "No content extracted"}


async def main():
    """Main function for single file testing."""
    
    print("📊 Single File Player Data Extraction Test")
    print("=" * 80)
    
    # Test configuration
    TEST_FILE = "gs://slams-app-bucket/SUMMER WORKOUT #16.png"
    TEST_DESCRIPTION = """This document contains summer workout basketball statistics including:
- Shooting stats (FGM, FGA, FG%, 3FGM, 3FGA, 3FG%, FTM, FTA, FT%)
- Game stats (Points, Rebounds, Assists, Turnovers, Steals, Blocks)  
- Advanced metrics (A/TO, OER, DER, Possessions)

The table shows players with jersey numbers like #13 Aponte, #30 Ball, #23 Cochran, etc.
Extract all visible players and their complete statistical data."""
    
    try:
        print(f"🧪 Testing File: {TEST_FILE}")
        print(f"📝 Expected Content: Summer workout basketball statistics")
        print("-" * 80)
        
        result = await test_single_file_extraction(TEST_FILE, TEST_DESCRIPTION)
        
        print(f"\n🎯 FINAL TEST RESULT")
        print("=" * 50)
        
        if result["success"]:
            print(f"✅ Test PASSED")
            print(f"👥 Successfully extracted {result['player_count']} players")
            
            # Save extracted data to file for review
            if result.get("data"):
                with open("extracted_player_data.json", "w") as f:
                    json.dump(result["data"], f, indent=2)
                print(f"💾 Full data saved to: extracted_player_data.json")
        else:
            print(f"❌ Test FAILED")
            print(f"🔍 Error: {result.get('error', 'Unknown error')}")
            
            # Save raw content for debugging
            if result.get("raw_content"):
                with open("debug_raw_content.txt", "w") as f:
                    f.write(result["raw_content"])
                print(f"🐛 Raw content saved to: debug_raw_content.txt")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n📊 Single file testing completed!")


if __name__ == "__main__":
    # You can easily change the test file here
    print("🔧 Single File Test Configuration:")
    print(f"📁 File: gs://slams-app-bucket/SUMMER WORKOUT #16.png")
    print(f"📊 Type: Summer Workout Basketball Statistics")
    print()
    
    # Run the test
    asyncio.run(main())