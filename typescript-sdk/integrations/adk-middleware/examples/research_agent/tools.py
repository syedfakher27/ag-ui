from google.adk.tools import google_search,url_context
from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool


search_agent = LlmAgent(
    name="google_search_agent",
    model="gemini-2.5-flash",
    description="Agent to answer questions using Google Search.",
    instruction="I can answer your questions by searching the internet. Just ask me anything!",
    tools=[google_search],
)

url_agent = LlmAgent(
    name="url_search_agent",
    model="gemini-2.5-flash",
    description="Agent to answer questions by scrapping from a given link",
    instruction="I can answer your questions by scrapping through a given web link. Just ask me anything!",
    tools=[url_context],
)


search_tool = agent_tool.AgentTool(agent=search_agent)
url_tool = agent_tool.AgentTool(agent=url_agent)