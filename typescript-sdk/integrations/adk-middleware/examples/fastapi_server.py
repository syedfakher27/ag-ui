#!/usr/bin/env python

"""Example FastAPI server using ADK middleware.

This example shows how to use the ADK middleware with FastAPI.
Note: Requires google.adk to be installed and configured.
"""

import uvicorn
from dotenv import load_dotenv
load_dotenv()
import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from .human_in_the_loop.agent import basketball_agent 
from .widgets_agent.agent import basket_ball_widget_agent 
from .email_conversation.agent import email_agent
from google.adk.sessions import DatabaseSessionService
from google.adk.artifacts import GcsArtifactService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.adk.memory import VertexAiMemoryBankService
import os
from pydantic import BaseModel
from google.adk.events import Event
from .helpers import adk_events_to_langchain_messages
import psycopg2
import psycopg2.extras
# import google.generativeai as genai
from google import genai
from google.genai import types
import math
from contextlib import contextmanager

class AgentRequest(BaseModel):
    name : str
    threadId: str
    properties :dict

class InsertChatRequest(BaseModel):
    user_id: str
    session_id: str
    query: str

class ChatSession(BaseModel):
    session_id: str
    chat_title: str
    created_at: str

class PaginatedChatResponse(BaseModel):
    sessions: list[ChatSession]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    
class ChatClearRequest(BaseModel):
    session_id: str
    delete_state: bool = False

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# These imports will work once google.adk is available
try:
    # from src.adk_agent import ADKAgent
    # from src.agent_registry import AgentRegistry
    # from src.endpoint import add_adk_fastapi_endpoint

    from adk_middleware import ADKAgent, AgentRegistry, add_adk_fastapi_endpoint
    from google.adk.agents import LlmAgent
    from google.adk import tools as adk_tools
    
    # Set up the agent registry
    registry = AgentRegistry.get_instance()
    
    # Create a sample ADK agent (this would be your actual agent)
    sample_agent = LlmAgent(
        name="assistant",
        model="gemini-2.0-flash",
        instruction="You are a helpful assistant.",
        tools=[adk_tools.preload_memory_tool.PreloadMemoryTool()]
    )
    # Register the agent
    registry.set_default_agent(sample_agent)
    registry.register_agent('adk-human-in-loop-agent', basketball_agent)
    registry.register_agent('adk-construction-project-agent', basket_ball_widget_agent)
    registry.register_agent('adk-email-agent', email_agent)

 
    
    @contextmanager
    def get_db_connection():
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(PG_CONNECTION_STRING)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    async def generate_chat_title(query: str) -> str:
        """Generate a chat title using Gemini API"""
        try:
            project_id = os.environ.get('GOOGLE_CLOUD_PROJECT','slamsportsai')
            location = os.environ.get('GOOGLE_CLOUD_LOCATION','us-central1')
            client = genai.Client(
                vertexai=True,
                project=project_id,
                location=location,
            )
            generate_content_config = types.GenerateContentConfig(
                temperature = 1,
                top_p = 0.95,
                max_output_tokens = 65535,
                safety_settings = [types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="OFF"
                ),types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="OFF"
                ),types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="OFF"
                ),types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="OFF"
                )],
                thinking_config=types.ThinkingConfig(
                thinking_budget=0,
                ),
            )
            prompt = f"Generate a concise, descriptive title (max 50 characters) for this chat query: '{query}'. Return only the title, no additional text."
            contents = [
                types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt)
                ]
                )
            ]
            response = client.models.generate_content(model='gemini-2.5-flash',config=generate_content_config,contents=contents)
            all_text = ""
            for candidate in response.candidates:
                 for part in candidate.content.parts:
                    all_text += part.text
            return all_text[:50]  # Ensure max 50 characters
        except Exception as e:
            logging.error(f"Error generating chat title: {e}")
            return query[:50]  # Fallback to truncated query
    
    PG_CONNECTION_STRING = os.environ.get('PG_CONNECTION_STRING')
    
    # Test database connection at startup
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                logging.info("Database connection established successfully")
    except Exception as e:
        logging.error(f"Failed to connect to database: {e}")
        logging.error("Please check your database connection string and ensure the database is running")
    
    session_service = DatabaseSessionService(db_url=PG_CONNECTION_STRING)
  
    memory_service = VertexAiMemoryBankService(project=os.environ.get('GOOGLE_CLOUD_PROJECT','slamsportsai'),location=os.environ.get('GOOGLE_CLOUD_LOCATION','us-central1'))
    artifact_service = GcsArtifactService(bucket_name='slams-app-bucket')
    # Create ADK middleware agent
    adk_agent = ADKAgent(
        app_name="demo_app",
        user_id="demo_user",
        session_timeout_seconds=604800,
        use_in_memory_services=False,
        session_service = session_service,
        memory_service = memory_service,
        credential_service=InMemoryCredentialService(),
        artifact_service=artifact_service,
        cleanup_interval_seconds=604800
    )
    
    adk_human_in_loop_agent = ADKAgent(
        app_name="demo_app",
        user_id="demo_user",
        session_timeout_seconds=604800,
        use_in_memory_services=False,
        session_service = session_service,
        memory_service = memory_service,
        credential_service=InMemoryCredentialService(),
        artifact_service=artifact_service,
        cleanup_interval_seconds=604800
    )
    adk_email_agent = ADKAgent(
        app_name="demo_app",
        user_id="demo_user",
        session_timeout_seconds=604800,
        use_in_memory_services=False,
        session_service = session_service,
        memory_service = memory_service,
        credential_service=InMemoryCredentialService(),
        artifact_service=artifact_service,
        cleanup_interval_seconds=604800
    )
    
    adk_construction_project_agent = ADKAgent(
        app_name="demo_app",
        user_id="demo_user",
        session_timeout_seconds=604800,
        use_in_memory_services=False,
        memory_service = memory_service,
        credential_service=InMemoryCredentialService(),
        session_service=session_service,
        artifact_service=artifact_service,
        cleanup_interval_seconds=604800
    )
    

    
    # Create FastAPI app
    app = FastAPI(title="ADK Middleware Demo")
    
    # Add CORS middleware to allow all origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )
    
    # Add the ADK endpoint
    add_adk_fastapi_endpoint(app, adk_agent, path="/chat")
    add_adk_fastapi_endpoint(app, adk_human_in_loop_agent, path="/adk-human-in-loop-agent")
    add_adk_fastapi_endpoint(app, adk_email_agent, path="/adk-email-agent")
    add_adk_fastapi_endpoint(app, adk_construction_project_agent, path="/adk-construction-project-agent")
    
    @app.get("/")
    async def root():
        return {"message": "ADK Middleware is running!", "endpoint": "/adk-human-in-loop-agent"}
    

    @app.get("/agents/state")
    async def agent_state(threadId:str):
        print('threadId',threadId)
        session = await session_service.get_session(app_name='demo_app',user_id='demo_user',session_id=threadId)
        if not session:
            return {"messages":[],"state":{}}
        events =session.events
        state =session.state
        langchain_messages = adk_events_to_langchain_messages(events)
        return {"messages":langchain_messages,"state":state}
    
    @app.post("/clear-chat")
    async def clear_chat(request: ChatClearRequest):
        try:
            session = await session_service.get_session(app_name='demo_app',user_id='demo_user',session_id=request.session_id)
            
            if request.delete_state:
                # Delete state completely - create empty session
                await session_service.delete_session(app_name='demo_app',user_id='demo_user',session_id=request.session_id)
                new_session = await session_service.create_session(app_name='demo_app',user_id='demo_user',state={},session_id=request.session_id)
                return {"success":True , "message":"chat history and state cleared completely"}
            else:
                # Keep existing state behavior
                state = session.state
                events = session.events
                
                await session_service.delete_session(app_name='demo_app',user_id='demo_user',session_id=request.session_id)
                new_session = await session_service.create_session(app_name='demo_app',user_id='demo_user',state=state,session_id=request.session_id)
                return {"success":True , "message":"chat history is cleared now"}
        except Exception as e:
            logging.error(f"Error inserting chat session: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
    @app.post("/insert_chat")
    async def insert_chat(request: InsertChatRequest):
        """Insert a new chat session with auto-generated title"""
        try:
            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    # Check if session_id already exists for this user
                    cursor.execute(
                        "SELECT session_id FROM user_session WHERE user_id = %s AND session_id = %s",
                        (request.user_id, request.session_id)
                    )
                    existing_session = cursor.fetchone()
                    
                    if existing_session:
                        logging.info(f"Session {request.session_id} already exists for user {request.user_id}, skipping insertion")
                        return {"message": "Session already exists, skipped insertion", "session_id": request.session_id}
                    
                    # Generate chat title using Gemini API
                    chat_title = await generate_chat_title(request.query)
                    
                    # Insert new session
                    cursor.execute(
                        """
                        INSERT INTO user_session (user_id, session_id, chat_title) 
                        VALUES (%s, %s, %s)
                        """,
                        (request.user_id, request.session_id, chat_title)
                    )
                    conn.commit()
                    
                    logging.info(f"Successfully inserted session {request.session_id} for user {request.user_id}")
                    return {
                        "message": "Chat session inserted successfully",
                        "user_id": request.user_id,
                        "session_id": request.session_id,
                        "chat_title": chat_title
                    }
                
        except Exception as e:
            logging.error(f"Error inserting chat session: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    @app.get("/chat_sessions", response_model=PaginatedChatResponse)
    async def get_chat_sessions(
        user_id: str = Query(..., description="User ID to fetch sessions for"),
        page: int = Query(1, ge=1, description="Page number (starts from 1)"),
        page_size: int = Query(10, ge=1, le=100, description="Number of sessions per page (max 100)")
    ):
        """Get paginated chat sessions for a user ordered by creation date"""
        try:
            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    # Calculate offset for pagination
                    offset = (page - 1) * page_size
                    
                    # Get total count of sessions for this user
                    cursor.execute(
                        "SELECT COUNT(*) FROM user_session us inner join sessions ss on ss.id =  us.session_id WHERE us.user_id = %s",
                        (user_id,)
                    )
                    count_result = cursor.fetchone()
                    count_result.get
                    print('total_count==>', count_result)
                    total_count = count_result.get('count')
                    print('total_count==>', total_count)
                    # Get paginated sessions ordered by created_at DESC (newest first)
                    cursor.execute(
                        """
                        SELECT session_id, chat_title, created_at 
                        FROM user_session  us inner join sessions ss on ss.id =  us.session_id
                        WHERE us.user_id = %s 
                        ORDER BY created_at DESC 
                        LIMIT %s OFFSET %s
                        """,
                        (user_id, page_size, offset)
                    )
                    sessions_data = cursor.fetchall()
                    
                    # Convert to ChatSession objects
                    sessions = [
                        ChatSession(
                            session_id=row['session_id'],
                            chat_title=row['chat_title'] or "",
                            created_at=row['created_at'].isoformat()
                        )
                        for row in sessions_data
                    ]
                    
                    # Calculate total pages
                    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0
                    
                    logging.info(f"Retrieved {len(sessions)} sessions for user {user_id}, page {page}")
                    
                    return PaginatedChatResponse(
                        sessions=sessions,
                        total_count=total_count,
                        page=page,
                        page_size=page_size,
                        total_pages=total_pages
                    )
                
        except psycopg2.Error as e:
            logging.error(f"Database error fetching chat sessions: {e}")
            raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
        except Exception as e:
            logging.error(f"Error fetching chat sessions: {e}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    if __name__ == "__main__":
        print("Starting ADK Middleware server...")
        print("Chat endpoint available at: http://localhost:8000/chat")
        print("API docs available at: http://localhost:8000/docs")
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
except ImportError as e:
    print(f"Cannot run server: {e}")
    print("Please install google.adk and ensure all dependencies are available.")
    print("\nTo install dependencies:")
    print("  pip install google-adk")
    print("  # Note: google-adk may not be publicly available yet")