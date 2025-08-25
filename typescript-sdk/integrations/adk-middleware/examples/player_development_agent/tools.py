import os
import json
from typing import Dict, Any, List
from google.cloud import discoveryengine_v1alpha as discoveryengine
from google.protobuf.json_format import MessageToDict

project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', "slamsportsai")
# engine_id = os.environ.get('DATASTORE_ID', "slams-player-stats")

def create_search_request(serving_config, search_query, meta_data, content_search_spec, boost_spec=None, facet_keys=[], enable_tuning=False):
    offset = (search_query.page_number - 1) * search_query.page_size
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
        "facet_specs": [
            discoveryengine.SearchRequest.FacetSpec(
                facet_key=discoveryengine.SearchRequest.FacetSpec.FacetKey(key=key),
                limit=100
            ) for key in facet_keys
        ],
        "custom_fine_tuning_spec": discoveryengine.CustomFineTuningSpec(
            enable_search_adaptor=enable_tuning
        )
    }

    if boost_spec is not None:
        request_data["boost_spec"] = boost_spec

    request = discoveryengine.SearchRequest(**request_data)
    return request

def build_metadata_filter(meta_data: Dict[str, Any]) -> str:
    """
    Build metadata filter in the correct format for Discovery Engine.
    Single values and lists are both wrapped in ANY() function.
    
    Examples:
    - {"player_name": "hinton"} -> 'player_name: ANY("hinton")'
    - {"player_name": ["hinton", "john"]} -> 'player_name: ANY("hinton", "john")'
    - {"player_name": "hinton", "data_type": "attributes"} -> 'player_name: ANY("hinton") AND data_type: ANY("attributes")'
    """
    def flatten_and_build_filters(d, parent_key=''):
        filters = []
        for k, v in d.items():
            full_key = f"{parent_key}.{k}" if parent_key else k

            if isinstance(v, dict):
                # Handle nested dictionaries
                filters.extend(flatten_and_build_filters(v, full_key))

            elif isinstance(v, list):
                if v and all(isinstance(item, (str, int, float, bool)) for item in v):
                    # Use double quotes for the values, ensuring proper escaping
                    values = ", ".join(f'"{str(item)}"' for item in v)
                    filters.append(f"{full_key}: ANY({values})")

            elif isinstance(v, (str, int, float, bool)):
                # Handle single values - also wrap in ANY() for consistency
                filters.append(f"{full_key}: ANY(\"{str(v)}\")")

        return filters

    filters = flatten_and_build_filters(meta_data)
    return ' AND '.join(filters)

def search_player_development_tool(query: str, meta_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search for player stats and attributes using Google Vertex AI Discovery Engine Client Library.
    
    Args:
        query: Search query to find relevant player data
        meta_data: Optional dictionary for building structured filters
    
    Returns:
        Dictionary containing search results with player stats/attributes information
    """
    try:
        # Build filter string
        metadata_filter = ""
        if meta_data:
            metadata_filter = build_metadata_filter(meta_data)
            print("Metadata filter:", metadata_filter)
        # metadata_filter = "player_name: ANY(\"hinton\")"
        # Initialize the Discovery Engine client
        client = discoveryengine.SearchServiceClient()
        location = "global"
        serving_config_id = "default_search"

        # Build the serving config path
        serving_config = client.serving_config_path(
            project=project_id,
            location=location,
            data_store="slams-player-stats",
            serving_config=serving_config_id,
        )

        # Prepare content search spec
        content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
            extractive_content_spec = discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                max_extractive_segment_count=5,
                return_extractive_segment_score=True
            )
        )

        # Prepare the search query object
        class SearchQuery:
            def __init__(self, query, page_size):
                self.query = query
                self.page_size = page_size
                self.page_number = 1
                self.next_page_token = ""

        search_query = SearchQuery(query, 10)

        # Create search request
        request = create_search_request(
            serving_config=serving_config,
            search_query=search_query,
            meta_data=metadata_filter,
            content_search_spec=content_search_spec
        )

        # Perform the search
        response = client.search(request=request)

        players_data = []
        total_size = 0
        corrected_query = ""
        query_expansion_used = False

        for search_result in response.results:
            document_dict = MessageToDict(search_result.document._pb, preserving_proto_field_name=True)
            # try:
            #     with open('latest_document.json', 'w') as f:
            #         json.dump(document_dict, f, indent=2, default=str)
            #     print(f"Saved document to latest_document.json")
            # except Exception as write_error:
            #     print(f"Failed to write document: {write_error}")
            struct_data = document_dict.get("struct_data", {})
            derived_struct_data = document_dict.get("derived_struct_data", {})
            # Extract extractive segments from derived_struct_data
            extractive_segments = derived_struct_data.get("extractive_segments", [])

            # Build relevant context from extractive answers
            relevant_context = []
            for segment in extractive_segments:
                context_item = {
                    "content": segment.get("content", ""),
                    "relevance_score": segment.get("relevanceScore", 0.1),
                    "source_title": derived_struct_data.get("title", "")
                }
                relevant_context.append(context_item)

            player_info = {
                "id": document_dict.get("id", ""),
                "player_name": struct_data.get("player_name", ""),
                "team": struct_data.get("team", ""),
                "sports": struct_data.get("sports", ""),
                "data_type": struct_data.get("data_type", ""),
                "recorded_date": struct_data.get("recorded_date", ""),
                "player_data": struct_data.get("player_data", {}),
                "relevant_context": relevant_context 
            }

            players_data.append(player_info)

        # Extract metadata from response
        total_size = getattr(response, 'total_size', 0)
        corrected_query = getattr(response, 'corrected_query', "")
        query_expansion_used = bool(getattr(response.query_expansion_info, 'expanded_query', False))

        return {
            "status": "success",
            "query": query,
            "filters": metadata_filter,
            "total_results": len(players_data),
            "players": players_data,
            "search_metadata": {
                "query_expansion_used": query_expansion_used,
                "corrected_query": corrected_query,
                "total_size": total_size
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to search player data: {str(e)}",
            "query": query,
            "filters": metadata_filter,
            "players": []
        }

if __name__ == "__main__":
    # Test 1: Single value
    # meta_data = {"player_name": "hinton", "data_type": "attributes"}
    # print("Test 1:", build_metadata_filter(meta_data))

    # # Test 2: List value
    # meta_data = {"player_name": ["hinton", "john"], "data_type": "stats"}
    # print("Test 2:", build_metadata_filter(meta_data))

    print("\n Test A: Search player_name='hinton'")
    result_a = search_player_development_tool(
        query="hinton performance",
        meta_data={"player_name": "hinton"}
    )
    print("Status:", result_a["status"])
    print("Total Results:", result_a["total_results"])
    if result_a["status"] == "error":
        print("Error:", result_a["message"])
    else:
        for player in result_a["players"]:
            print(f"{player['player_name']} | Team: {player['team']} | Score: {player['relevance_score']:.3f}")
