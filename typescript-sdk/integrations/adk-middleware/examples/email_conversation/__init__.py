from .agent import email_agent
from .tools import fetch_email_by_name

__all__ = [
    'email_agent',
    'fetch_email_by_name'
]

__version__ = "1.0.0"
__author__ = "ADK Middleware Team"
__description__ = "Email conversation using ADK and Context7 MCP"