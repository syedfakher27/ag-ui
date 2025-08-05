import os
import json
from typing import Dict, Any, List
from google.cloud import storage
from google.cloud import discoveryengine_v1alpha as discoveryengine
from google.protobuf.json_format import MessageToDict

project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', "slamsportsai")
engine_id = os.environ.get('DATASTORE_ID', "slams-video-ds")

def analyze_player_relevance_tool(
    gcs_links: List[str], 
    selected_videos: List[Dict[str, Any]],
    selection_reasoning: str
) -> Dict[str, Any]:
    """
    Downloads analysis text content from GCS links and returns the raw content
    along with the selected relevant videos for rendering.
    
    Args:
        gcs_links: List of GCS links to analysis text files (gs://bucket/path/file.txt)
        selected_videos: List of video objects that were selected as most relevant
        selection_reasoning: Explanation of why these videos were selected
    
    Returns:
        Dictionary containing the downloaded analysis content and selected videos for UI rendering
    """
    try:
        # Initialize GCS client
        storage_client = storage.Client()
        
        analysis_files = []
        
        # Process each GCS file
        for gcs_link in gcs_links:
            if not gcs_link.startswith("gs://"):
                continue
                
            try:
                # Parse GCS path
                path_parts = gcs_link[5:].split("/", 1)  # Remove 'gs://' and split
                bucket_name = path_parts[0]
                blob_path = path_parts[1]
                
                # Get the file content
                bucket = storage_client.bucket(bucket_name)
                blob = bucket.blob(blob_path)
                
                if not blob.exists():
                    print(f"File not found: {gcs_link}")
                    analysis_files.append({
                        "file_link": gcs_link,
                        "file_name": blob_path.split("/")[-1],
                        "status": "not_found",
                        "content": "",
                        "error": f"File not found: {gcs_link}"
                    })
                    continue
                    
                # Download the content
                analysis_text = blob.download_as_text()
                
                analysis_files.append({
                    "file_link": gcs_link,
                    "file_name": blob_path.split("/")[-1],
                    "status": "success",
                    "content": analysis_text,
                    "content_length": len(analysis_text)
                })
                
                print(f"Successfully downloaded: {gcs_link} ({len(analysis_text)} characters)")
                
            except Exception as file_error:
                print(f"Error processing file {gcs_link}: {file_error}")
                analysis_files.append({
                    "file_link": gcs_link,
                    "file_name": gcs_link.split("/")[-1],
                    "status": "error",
                    "content": "",
                    "error": str(file_error)
                })
                continue
        
        return {
            "status": "success",
            "total_files_requested": len(gcs_links),
            "total_files_downloaded": len([f for f in analysis_files if f["status"] == "success"]),
            "analysis_files": analysis_files,
            "videos": selected_videos or [],
            "selection_reasoning": selection_reasoning,
            "query": "Selected Relevant Videos"  # For UI consistency
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to download analysis files: {str(e)}",
            "analysis_files": []
        }
    
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

def search_videos_tool(query: str,  meta_data: Dict[str, Any] ) -> Dict[str, Any]:
    """
    Search for relevant videos using Google Vertex AI Discovery Engine Client Library.
    
    Args:
        query: Search query to find relevant videos
        meta_data: Optional dictionary for building structured filters
    
    Returns:
        Dictionary containing search results with video information and analysis
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

        # Prepare content search spec (you can modify this if needed)
        content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec()

        # Prepare the search query object
        class SearchQuery:
            def __init__(self, query, page_size):
                self.query = query
                self.page_size = page_size
                self.page_number = 1
                self.next_page_token = ""

        search_query = SearchQuery(query,10)

        # Create search request using helper function
        request = create_search_request(
            serving_config=serving_config,
            search_query=search_query,
            meta_data=metadata_filter,
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
            derived_struct_data = document_dict.get("derived_struct_data", {}) 
            context_metadata = struct_data.get("context_metadata", {})

            video_info = {
                "id": document_dict.get("id", ""),
                "title": context_metadata.get("title", struct_data.get("analysis_title", "Unknown Title")),
                "description": context_metadata.get("description", "No description available"),
                "analysis_text_link" : derived_struct_data.get("link", ""),
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
            "filters": metadata_filter,
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
            "filters": metadata_filter,
            "videos": []
        }
