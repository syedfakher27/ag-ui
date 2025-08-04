import os
import json
from typing import Dict, Any
from google.cloud import discoveryengine_v1alpha as discoveryengine
from google.protobuf.json_format import MessageToDict

project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', "slamsportsai")
engine_id = os.environ.get('DATASTORE_ID', "slams-video-ds")


def create_search_request(serving_config, search_query, meta_data, content_search_spec, boost_spec=None, facet_keys=[], enable_tuning=False):
    # Base request without boost_spec
    offset = (search_query.page_number - 1) * search_query.page_size
    # #print("OFFSET", offset)
    request_data = {
        "serving_config": serving_config,
        "query": search_query.query,
        "page_size": search_query.page_size,
        "offset": offset,
        "page_token": search_query.next_page_token,
        "content_search_spec": content_search_spec,
        "query_expansion_spec": discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        "spell_correction_spec": discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
        "filter": meta_data,
        "facet_specs":  [
            discoveryengine.SearchRequest.FacetSpec(
                facet_key=discoveryengine.SearchRequest.FacetSpec.FacetKey(key=key),
                limit=100
            ) for key in facet_keys
        ],
        "custom_fine_tuning_spec": discoveryengine.CustomFineTuningSpec(
            enable_search_adaptor = enable_tuning
        )    
    }

    # Add boost_spec to the request if search_query.boost is True and boost_spec is provided
    if boost_spec is not None:
        request_data["boost_spec"] = boost_spec

    # Create the SearchRequest object with the dynamically constructed request data
    request = discoveryengine.SearchRequest(**request_data)

    return request

def build_metadata_filter(meta_data: Dict[str, Any]) -> str:
    def flatten_and_build_filters(d, parent_key=''):
        filters = []

        for k, v in d.items():
            full_key = f"{parent_key}.{k}" if parent_key else k

            if isinstance(v, dict):
                filters.extend(flatten_and_build_filters(v, full_key))

            elif isinstance(v, list):
                # Only allow list of primitives (e.g., strings, ints)
                if all(isinstance(item, (str, int, float, bool)) for item in v):
                    values = ', '.join(f'"{str(item)}"' for item in v)
                    filters.append(f'{full_key}: ANY({values})')

            elif isinstance(v, (str, int, float, bool)):
                filters.append(f'{full_key}: ANY("{str(v)}")')

        return filters

    return ' AND '.join(flatten_and_build_filters(meta_data))

def search_videos_tool(query: str, filters: str , meta_data: Dict[str, Any] , page_size: int) -> Dict[str, Any]:
    """
    Search for relevant videos using Google Vertex AI Discovery Engine Client Library.
    
    Args:
        query: Search query to find relevant videos
        filters: Optional filter expression string (e.g., 'sport="basketball"', 'players.name="John Doe"')
        meta_data: Optional dictionary for building structured filters
        page_size: Number of results to return (default: 10, max: 100)
    
    Returns:
        Dictionary containing search results with video information and analysis
    """
    try:
        # Build filter string
        final_filter = ""
        if meta_data:
            metadata_filter = build_metadata_filter(meta_data)
            print("Metadata filter:", metadata_filter)
            if filters and metadata_filter:
                final_filter = f"{filters} AND {metadata_filter}"
            elif metadata_filter:
                final_filter = metadata_filter
            elif filters:
                final_filter = filters
        elif filters:
            final_filter = filters

        # Initialize the Discovery Engine client
        client = discoveryengine.SearchServiceClient()
        location = "global"
        serving_config_id = "default_search"

        # Build the serving config path
        serving_config = client.serving_config_path(
            project=project_id,
            location=location,
            data_store=engine_id,
            serving_config=serving_config_id,
        )

        # Prepare content search spec (you can modify this if needed)
        content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec()

        # Prepare the search query object
        class SearchQuery:
            def __init__(self, query, page_size):
                self.query = query
                self.page_size = page_size
                self.page_number = 1
                self.next_page_token = ""

        search_query = SearchQuery(query, min(page_size, 10))

        # Create search request using helper function
        request = create_search_request(
            serving_config=serving_config,
            search_query=search_query,
            meta_data=final_filter,
            content_search_spec=content_search_spec
        )

        # Perform the search
        response = client.search(request=request)

        videos = []
        total_size = 0
        corrected_query = ""
        query_expansion_used = False

        for search_result in response.results:
            document_dict = MessageToDict(search_result.document._pb, preserving_proto_field_name=True)
            try:
                with open('latest_document.json', 'w') as f:
                    json.dump(document_dict, f, indent=2, default=str)
                print(f"Saved document to latest_document.json")
            except Exception as write_error:
                print(f"Failed to write document: {write_error}")
            struct_data = document_dict.get("struct_data", {})
            context_metadata = struct_data.get("context_metadata", {})

            video_info = {
                "id": document_dict.get("id", ""),
                "title": context_metadata.get("title", struct_data.get("analysis_title", "Unknown Title")),
                "description": context_metadata.get("description", "No description available"),
                "filename": context_metadata.get("filename", ""),
                "sport": context_metadata.get("sport", struct_data.get("sports", "")),
                "video_type": context_metadata.get("video_type", ""),
                "analysis_title": struct_data.get("analysis_title", ""),
                "player_id": struct_data.get("player_id", ""),
                "players": context_metadata.get("players", []),
                "teams": context_metadata.get("teams", []),
                "context_metadata": context_metadata,
                "technical_metadata": struct_data.get("technical_metadata", {}),
                "relevance_score": 0.0
            }

            # Extract relevance score
            if hasattr(search_result, 'model_scores') and search_result.model_scores:
                if 'relevance_score' in search_result.model_scores:
                    relevance_score_values = search_result.model_scores['relevance_score'].values
                    if relevance_score_values:
                        video_info["relevance_score"] = relevance_score_values[0]

            # Format players
            if isinstance(video_info["players"], list):
                formatted_players = []
                for player in video_info["players"]:
                    if isinstance(player, dict):
                        formatted_players.append({
                            "name": player.get("name", "Unknown"),
                            "position": player.get("position", ""),
                            "team": player.get("team", ""),
                            "jersey_number": str(player.get("jersey_number", "")),
                            "actions": player.get("actions", [])
                        })
                video_info["players"] = formatted_players

            # Format teams
            if isinstance(video_info["teams"], list):
                formatted_teams = []
                for team in video_info["teams"]:
                    if isinstance(team, dict):
                        formatted_teams.append({"name": team.get("name", "Unknown Team")})
                video_info["teams"] = formatted_teams

            videos.append(video_info)
        
        # Extract metadata from response
        total_size = getattr(response, 'total_size', 0)
        corrected_query = getattr(response, 'corrected_query', "")
        query_expansion_used = bool(getattr(response.query_expansion_info, 'expanded_query', False))

        return {
            "status": "success",
            "query": query,
            "filters": final_filter,
            "total_results": len(videos),
            "videos": videos,
            "search_metadata": {
                "query_expansion_used": query_expansion_used,
                "corrected_query": corrected_query,
                "total_size": total_size
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to search videos: {str(e)}",
            "query": query,
            "filters": filters,
            "videos": []
        }

def print_separator(title: str):
    """Print a formatted separator for test sections."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def print_result_summary(result: Dict[str, Any]):
    """Print a summary of search results."""
    if result["status"] == "success":
        print(f"✅ SUCCESS - Found {result['total_results']} videos")
        print(f"Query: '{result['query']}'")
        if result["filters"]:
            print(f"Filters: {result['filters']}")
        
        # Print search metadata
        metadata = result["search_metadata"]
        if metadata["corrected_query"]:
            print(f"Corrected Query: '{metadata['corrected_query']}'")
        if metadata["query_expansion_used"]:
            print("Query Expansion: Used")
        print(f"Total Available: {metadata['total_size']}")
        
        # Print video summaries
        for i, video in enumerate(result["videos"][:3], 1):  # Show first 3 videos
            print(f"\n📹 Video {i}: {video['title']}")
            print(f"   Sport: {video['sport']} | Type: {video['video_type']}")
            print(f"   Players: {len(video['players'])} | Relevance: {video['relevance_score']:.2f}")
            if video['players']:
                player_names = [p['name'] for p in video['players'][:3]]
                print(f"   Top Players: {', '.join(player_names)}")
    else:
        print(f"❌ ERROR: {result['message']}")


def run_tests():
    """Run comprehensive tests of the video search tool."""
    
    print("🎬 SLAM Video Search Tool - Test Suite")
    print("Testing Google Discovery Engine integration...")
    
    # Test cases with various scenarios
    test_cases = [
        
        {
            "name": "Sport Filter - Basketball Only",
            "query": "Myles highlights",
            "meta_data": {
            "context_metadata.players.name": ["Myles Foster"],
            "context_metadata.teams.name": [ "Clemson","Illinois State"
            ]
            }, "page_size": 10
    },
           
        # {
        #     "name": "Player Search",
        #     "query": "player analysis",
        #     "filters": "",
        #     "page_size": 5
        # },
        # {
        #     "name": "Complex Filter - Basketball Guards",
        #     "query": "performance",
        #     "filters": 'sport="basketball" AND players.position="guard"',
        #     "page_size": 3
        # },
        # {
        #     "name": "Video Type Filter",
        #     "query": "analysis",
        #     "filters": 'video_type="training"',
        #     "page_size": 5
        # },
        # {
        #     "name": "Large Page Size",
        #     "query": "sports",
        #     "filters": "",
        #     "page_size": 20
        # },
        # {
        #     "name": "Empty Query Test",
        #     "query": "",
        #     "filters": "",
        #     "page_size": 5
        # },
        # {
        #     "name": "Non-existent Sport",
        #     "query": "cricket",
        #     "filters": 'sport="cricket"',
        #     "page_size": 5
        # }
    ]
    
    # Run all test cases
    for i, test_case in enumerate(test_cases, 1):
        print_separator(f"Test {i}: {test_case['name']}")
        
        try:
            result = search_videos_tool(
                query=test_case["query"],
                meta_data=test_case["meta_data"],
                page_size=test_case["page_size"]
            )
            print_result_summary(result)
            
            # Additional validation
            if result["status"] == "success":
                assert isinstance(result["videos"], list), "Videos should be a list"
                assert result["total_results"] == len(result["videos"]), "Total results should match video count"
                
                for video in result["videos"]:
                    assert "id" in video, "Video should have an ID"
                    assert "title" in video, "Video should have a title"
                    assert isinstance(video["players"], list), "Players should be a list"
                
                print("Validation passed")
            
        except Exception as e:
            print(f"Test failed with exception: {str(e)}")


# Interactive testing functions
def test_basic_search():
    """Test basic search functionality."""
    print("Testing basic search...")
    result = search_videos_tool("basketball", page_size=5)
    print(json.dumps(result, indent=2))
    return result


def test_filtered_search():
    """Test search with filters."""
    print("Testing filtered search...")
    result = search_videos_tool(
        query="training", 
        filters='sport="basketball"', 
        page_size=5
    )
    print(json.dumps(result, indent=2))
    return result


def test_player_search():
    """Test player-specific search."""
    print("Testing player search...")
    result = search_videos_tool(
        query="player performance", 
        filters='players.position="guard"', 
        page_size=3
    )
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    # Run the comprehensive test suite
    run_tests()
    
    print("\n" + "="*60)
    print("INDIVIDUAL TEST FUNCTIONS AVAILABLE:")
    print("- test_basic_search()")
    print("- test_filtered_search()")
    print("- test_player_search()")
    print("="*60)