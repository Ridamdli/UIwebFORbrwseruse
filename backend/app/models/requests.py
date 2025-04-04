from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class AgentRunRequest(BaseModel):
    """Request model for running an agent task"""
    agent_type: str = Field(default="custom", description="Type of agent to use (org or custom)")
    llm_provider: str = Field(description="LLM provider (e.g., openai, anthropic)")
    llm_model_name: str = Field(description="Model name to use")
    llm_temperature: float = Field(default=0.6, description="Temperature for LLM")
    llm_num_ctx: int = Field(default=16000, description="Context length for Ollama models")
    llm_base_url: Optional[str] = Field(default=None, description="Base URL for LLM API")
    llm_api_key: Optional[str] = Field(default=None, description="API key for LLM provider")
    use_own_browser: bool = Field(default=False, description="Whether to use own browser")
    keep_browser_open: bool = Field(default=False, description="Whether to keep browser open between tasks")
    headless: bool = Field(default=False, description="Whether to run browser in headless mode")
    disable_security: bool = Field(default=True, description="Whether to disable browser security features")
    window_w: int = Field(default=1280, description="Browser window width")
    window_h: int = Field(default=1100, description="Browser window height")
    enable_recording: bool = Field(default=True, description="Whether to enable recording")
    max_steps: int = Field(default=100, description="Maximum number of steps for agent to take")
    use_vision: bool = Field(default=True, description="Whether to enable vision capabilities")
    max_actions_per_step: int = Field(default=10, description="Maximum number of actions per step")
    tool_calling_method: str = Field(default="auto", description="Tool calling method")
    chrome_cdp: Optional[str] = Field(default=None, description="Chrome CDP URL")
    max_input_tokens: int = Field(default=128000, description="Maximum input tokens")
    task: str = Field(description="Task description for the agent")
    add_infos: Optional[str] = Field(default="", description="Additional information for the agent")

class ResearchRequest(BaseModel):
    """Request model for running a research task"""
    research_task: str = Field(description="Research task description")
    max_search_iteration: int = Field(default=3, description="Maximum number of search iterations")
    max_query_per_iter: int = Field(default=1, description="Maximum number of queries per iteration")
    llm_provider: str = Field(description="LLM provider (e.g., openai, anthropic)")
    llm_model_name: str = Field(description="Model name to use")
    llm_temperature: float = Field(default=0.6, description="Temperature for LLM")
    llm_num_ctx: int = Field(default=16000, description="Context length for Ollama models")
    llm_base_url: Optional[str] = Field(default=None, description="Base URL for LLM API")
    llm_api_key: Optional[str] = Field(default=None, description="API key for LLM provider")
    use_vision: bool = Field(default=True, description="Whether to enable vision capabilities")
    use_own_browser: bool = Field(default=False, description="Whether to use own browser")
    headless: bool = Field(default=False, description="Whether to run browser in headless mode")
    chrome_cdp: Optional[str] = Field(default=None, description="Chrome CDP URL")

class GetRecordingsRequest(BaseModel):
    """Request model for getting recordings"""
    pass 