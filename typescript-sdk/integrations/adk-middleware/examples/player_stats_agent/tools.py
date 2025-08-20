import os
import json
from typing import Dict, Any, List
from google.cloud import discoveryengine_v1alpha as discoveryengine
from google.protobuf.json_format import MessageToDict

project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', "slamsportsai")
engine_id = os.environ.get('DATASTORE_ID', "slams-player-stats")

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
    def flatten_and_build_filters(d, parent_key=''):
        filters = []

        for k, v in d.items():
            full_key = f"{parent_key}.{k}" if parent_key else k

            if isinstance(v, dict):
                filters.extend(flatten_and_build_filters(v, full_key))
            elif isinstance(v, list):
                if all(isinstance(item, (str, int, float, bool)) for item in v):
                    values = ', '.join(f'"{str(item)}"' for item in v)
                    filters.append(f'{full_key}: ANY({values})')
            elif isinstance(v, (str, int, float, bool)):
                filters.append(f'{full_key}: ANY("{str(v)}")')

        return filters

    return ' AND '.join(flatten_and_build_filters(meta_data))

def search_player_stats_tool(query: str, meta_data: Dict[str, Any]) -> Dict[str, Any]:
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

        # Prepare content search spec
        content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec()

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
            
            try:
                with open('latest_player_document.json', 'w') as f:
                    json.dump(document_dict, f, indent=2, default=str)
                print(f"Saved document to latest_player_document.json")
            except Exception as write_error:
                print(f"Failed to write document: {write_error}")
            
            struct_data = document_dict.get("struct_data", {})
            content = document_dict.get("content", {})

            player_info = {
                "id": document_dict.get("id", ""),
                "player_name": struct_data.get("player_name", "Unknown Player"),
                "team": struct_data.get("team", ""),
                "sports": struct_data.get("sports", ""),
                "data_type": struct_data.get("data_type", ""),
                "recorded_date": struct_data.get("recorded_date", ""),
                "source_file": struct_data.get("source_file", ""),
                "player_data": struct_data.get("player_data", {}),
                "content_uri": content.get("uri", ""),
                "mime_type": content.get("mimeType", ""),
                "relevance_score": 0.0
            }

            # Extract relevance score
            if hasattr(search_result, 'model_scores') and search_result.model_scores:
                if 'relevance_score' in search_result.model_scores:
                    relevance_score_values = search_result.model_scores['relevance_score'].values
                    if relevance_score_values:
                        player_info["relevance_score"] = relevance_score_values[0]

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