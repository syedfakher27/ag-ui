import uuid
from typing import List, Dict, Any, Optional
import json
from google.adk.events import Event as ADKEvent

def adk_events_to_langchain_messages(events: List[ADKEvent]) -> List[Dict[str, Any]]:
    """
    Convert ADK events to LangChain message format.
    
    Args:
        events: List of ADK events from the session
        
    Returns:
        List of LangChain messages in the format expected by langchainMessagesToCopilotKit
    """
    langchain_messages = []
    
    # Track state for message construction
    current_ai_message_id = None
    current_ai_content = ""
    current_tool_calls = []
    pending_tool_results = {}  # tool_call_id -> result content
    
    for event in events:
        try:
            # Skip events without author
            if not hasattr(event, 'author') or not event.author:
                continue
                
            # Handle user messages
            if event.author == "user":
                user_content = _extract_text_content(event)
                if user_content:
                    langchain_messages.append({
                        "type": "human",
                        "content": user_content,
                        "id": getattr(event, 'id', str(uuid.uuid4()))
                    })
            
            # Handle system messages (if any agent acts as system)
            elif event.author == "system":
                system_content = _extract_text_content(event)
                if system_content:
                    langchain_messages.append({
                        "type": "system",
                        "content": system_content,
                        "id": getattr(event, 'id', str(uuid.uuid4()))
                    })
            
            # Handle assistant/agent messages
            else:
                # This is an assistant/agent message
                event_id = getattr(event, 'id', str(uuid.uuid4()))
                
                # Check for function calls using ADK method
                function_calls = event.get_function_calls() if hasattr(event, 'get_function_calls') else []
                
                # Check for function responses using ADK method  
                function_responses = event.get_function_responses() if hasattr(event, 'get_function_responses') else []
                
                # Extract text content
                text_content = _extract_text_content(event)
                
                # Handle function responses (tool results)
                if function_responses:
                    for func_response in function_responses:
                        tool_call_id = getattr(func_response, 'id', str(uuid.uuid4()))
                        result_content = func_response.response
                        
                        # Convert result to string if needed
                        if isinstance(result_content, dict):
                            result_content = json.dumps(result_content)
                        elif not isinstance(result_content, str):
                            result_content = str(result_content)
                        
                        # Add tool result message
                        langchain_messages.append({
                            "type": "tool",
                            "content": result_content,
                            "tool_call_id": tool_call_id,
                            "name": getattr(func_response, 'name', ''),
                            "id": str(uuid.uuid4())
                        })
                
                # Handle function calls (tool requests)
                elif function_calls:
                    # Create AI message with tool calls
                    tool_calls_list = []
                    for func_call in function_calls:
                        
                        tool_call_id = getattr(func_call, 'id', str(uuid.uuid4()))
                        tool_calls_list.append({
                            "id": tool_call_id,
                            "name": func_call.name,
                            "args": getattr(func_call, 'args', {})
                        })
                    
                    langchain_messages.append({
                        "type": "ai",
                        "content": text_content or "",
                        "tool_calls": tool_calls_list,
                        "id": event_id
                    })
                
                # Handle regular text messages
                elif text_content and event.is_final_response():
                    # Only add final responses to avoid duplicate streaming content
                    langchain_messages.append({
                        "type": "ai",
                        "content": text_content,
                        "id": event_id,
                        "tool_calls":[]
                    })
                
                # Skip partial/streaming events that aren't final responses
                # as they would create duplicate content
                    
        except Exception as e:
            # Log error but continue processing
            print(f"Error processing event {getattr(event, 'id', 'unknown')}: {e}")
            continue
    
    return langchain_messages


def _extract_text_content(event: ADKEvent) -> str:
    """Extract text content from an ADK event."""
    text_parts = []
    
    # Check if event has content and parts
    if hasattr(event, 'content') and event.content:
        if hasattr(event.content, 'parts') and event.content.parts:
            for part in event.content.parts:
                # Check for text content in the part
                if hasattr(part, 'text') and part.text:
                    text_parts.append(part.text)
    
    return "".join(text_parts)


# Usage in your code:
# def convert_session_events_to_langchain(agent_request):
#     """Convert session events to LangChain messages."""
#     events = session_service.get_session(agent_request.threadId).events
#     langchain_messages = adk_events_to_langchain_messages(events)
#     return langchain_messages


# Example usage:
# events = session_service.get_session(agent_request.threadId).events  
# langchain_messages = adk_events_to_langchain_messages(events)