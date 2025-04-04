import asyncio
import os
import sys
import glob
import base64
from typing import Dict, List, Optional, Any, Callable

# Add the project root to the Python path so we can import from the original project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Import from the original project
from src.utils import utils
from src.agent.custom_agent import CustomAgent
from src.agent.custom_prompts import CustomSystemPrompt, CustomAgentMessagePrompt
from src.controller.custom_controller import CustomController
from src.browser.custom_browser import CustomBrowser
from src.browser.custom_context import BrowserContextConfig
from browser_use.browser.browser import BrowserConfig
from browser_use.browser.context import BrowserContextWindowSize
from src.utils.deep_research import deep_research

# Global variables for browser instances
_global_browser = None
_global_browser_context = None
_global_agent = None

async def run_browser_agent(
    agent_type: str,
    llm_provider: str,
    llm_model_name: str,
    llm_num_ctx: int,
    llm_temperature: float,
    llm_base_url: Optional[str],
    llm_api_key: Optional[str],
    use_own_browser: bool,
    keep_browser_open: bool,
    headless: bool,
    disable_security: bool,
    window_w: int,
    window_h: int,
    enable_recording: bool,
    task: str,
    add_infos: str,
    max_steps: int,
    use_vision: bool,
    max_actions_per_step: int,
    tool_calling_method: str,
    chrome_cdp: Optional[str],
    max_input_tokens: int,
    on_update: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    Run the browser agent and return the result.
    This is a bridge function that adapts our new API to the existing code.
    """
    global _global_browser, _global_browser_context, _global_agent
    
    try:
        # Set up recording path based on enable_recording flag
        save_recording_path = "./tmp/record_videos" if enable_recording else None
        save_agent_history_path = "./tmp/agent_history"
        save_trace_path = "./tmp/traces"

        # Ensure directories exist
        if save_recording_path:
            os.makedirs(save_recording_path, exist_ok=True)
        if save_agent_history_path:
            os.makedirs(save_agent_history_path, exist_ok=True)
        if save_trace_path:
            os.makedirs(save_trace_path, exist_ok=True)

        # Get the list of existing videos before the agent runs
        existing_videos = set()
        if save_recording_path:
            existing_videos = set(
                glob.glob(os.path.join(save_recording_path, "*.[mM][pP]4"))
                + glob.glob(os.path.join(save_recording_path, "*.[wW][eE][bB][mM]"))
            )

        # Get the LLM model
        llm = utils.get_llm_model(
            provider=llm_provider,
            model_name=llm_model_name,
            num_ctx=llm_num_ctx,
            temperature=llm_temperature,
            base_url=llm_base_url,
            api_key=llm_api_key,
        )

        # Call the appropriate function based on agent_type
        if agent_type == "custom":
            result = await run_custom_agent(
                llm=llm,
                use_own_browser=use_own_browser,
                keep_browser_open=keep_browser_open,
                headless=headless,
                disable_security=disable_security,
                window_w=window_w,
                window_h=window_h,
                save_recording_path=save_recording_path,
                save_agent_history_path=save_agent_history_path,
                save_trace_path=save_trace_path,
                task=task,
                add_infos=add_infos,
                max_steps=max_steps,
                use_vision=use_vision,
                max_actions_per_step=max_actions_per_step,
                tool_calling_method=tool_calling_method,
                chrome_cdp=chrome_cdp,
                max_input_tokens=max_input_tokens,
                on_update=on_update
            )
        else:  # "org" agent type
            raise ValueError(f"Agent type '{agent_type}' is not supported in this version.")

        return result
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        return {
            "final_result": "",
            "errors": error_msg,
            "model_actions": "",
            "model_thoughts": "",
            "recording_path": None,
            "trace_file": None,
            "history_file": None
        }
    finally:
        # Clean up resources if not keeping browser open
        if not keep_browser_open:
            await cleanup_browser()

async def run_custom_agent(
    llm,
    use_own_browser,
    keep_browser_open,
    headless,
    disable_security,
    window_w,
    window_h,
    save_recording_path,
    save_agent_history_path,
    save_trace_path,
    task,
    add_infos,
    max_steps,
    use_vision,
    max_actions_per_step,
    tool_calling_method,
    chrome_cdp,
    max_input_tokens,
    on_update=None
):
    """Run the custom agent implementation"""
    global _global_browser, _global_browser_context, _global_agent

    try:
        extra_chromium_args = [f"--window-size={window_w},{window_h}"]
        cdp_url = chrome_cdp
        if use_own_browser:
            cdp_url = os.getenv("CHROME_CDP", chrome_cdp)
            chrome_path = os.getenv("CHROME_PATH", None)
            if chrome_path == "":
                chrome_path = None
            chrome_user_data = os.getenv("CHROME_USER_DATA", None)
            if chrome_user_data:
                extra_chromium_args += [f"--user-data-dir={chrome_user_data}"]
        else:
            chrome_path = None

        controller = CustomController()

        # Initialize global browser if needed
        if (_global_browser is None) or (cdp_url and cdp_url != ""):
            _global_browser = CustomBrowser(
                config=BrowserConfig(
                    headless=headless,
                    disable_security=disable_security,
                    cdp_url=cdp_url,
                    chrome_instance_path=chrome_path,
                    extra_chromium_args=extra_chromium_args,
                )
            )

        if _global_browser_context is None or (chrome_cdp and cdp_url != ""):
            _global_browser_context = await _global_browser.new_context(
                config=BrowserContextConfig(
                    trace_path=save_trace_path if save_trace_path else None,
                    save_recording_path=save_recording_path if save_recording_path else None,
                    no_viewport=False,
                    browser_window_size=BrowserContextWindowSize(
                        width=window_w, height=window_h
                    ),
                )
            )

        # Create and run agent
        _global_agent = CustomAgent(
            task=task,
            add_infos=add_infos,
            use_vision=use_vision,
            llm=llm,
            browser=_global_browser,
            browser_context=_global_browser_context,
            controller=controller,
            system_prompt_class=CustomSystemPrompt,
            agent_prompt_class=CustomAgentMessagePrompt,
            max_actions_per_step=max_actions_per_step,
            tool_calling_method=tool_calling_method,
            max_input_tokens=max_input_tokens,
            generate_gif=True
        )

        # Set up a task for periodic screenshot capture if on_update is provided
        if on_update:
            screenshot_task = asyncio.create_task(periodic_screenshot_capture(_global_browser_context, _global_agent, on_update))

        # Run the agent
        history = await _global_agent.run(max_steps=max_steps)

        # Save history
        history_file = os.path.join(save_agent_history_path, f"{_global_agent.state.agent_id}.json")
        _global_agent.save_history(history_file)

        # Prepare the result
        final_result = history.final_result()
        errors = history.errors()
        model_actions = history.model_actions()
        model_thoughts = history.model_thoughts()

        # Get the latest trace file
        trace_file = utils.get_latest_files(save_trace_path)
        trace_file_path = trace_file.get('.zip')

        # Get the latest recording file
        latest_recording = None
        if save_recording_path:
            new_videos = set(
                glob.glob(os.path.join(save_recording_path, "*.[mM][pP]4"))
                + glob.glob(os.path.join(save_recording_path, "*.[wW][eE][bB][mM]"))
            )
            if new_videos - existing_videos:
                latest_recording = list(new_videos - existing_videos)[0]

        # Final update to the client
        if on_update:
            on_update({
                "progress": 1.0,
                "final_result": final_result,
                "errors": errors,
                "model_actions": model_actions,
                "model_thoughts": model_thoughts,
                "recording_path": latest_recording,
                "trace_file": trace_file_path,
                "history_file": history_file
            })

        return {
            "final_result": final_result,
            "errors": errors,
            "model_actions": model_actions,
            "model_thoughts": model_thoughts,
            "recording_path": latest_recording,
            "trace_file": trace_file_path,
            "history_file": history_file
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        errors = f"{str(e)}\n{traceback.format_exc()}"
        return {
            "final_result": "",
            "errors": errors,
            "model_actions": "",
            "model_thoughts": "",
            "recording_path": None,
            "trace_file": None,
            "history_file": None
        }
    finally:
        _global_agent = None
        # Handle cleanup based on persistence configuration
        if not keep_browser_open:
            await cleanup_browser()

async def run_deep_research(
    research_task,
    max_search_iteration,
    max_query_per_iter,
    llm_provider,
    llm_model_name,
    llm_num_ctx,
    llm_temperature,
    llm_base_url,
    llm_api_key,
    use_vision,
    use_own_browser,
    headless,
    chrome_cdp,
    on_update=None
):
    """Bridge function to run the deep_research function from the original project"""
    try:
        # Get the LLM model
        llm = utils.get_llm_model(
            provider=llm_provider,
            model_name=llm_model_name,
            num_ctx=llm_num_ctx,
            temperature=llm_temperature,
            base_url=llm_base_url,
            api_key=llm_api_key,
        )

        # Create a fake agent state to pass to deep_research
        from src.utils.agent_state import AgentState
        agent_state = AgentState()

        # Set up progress reporting
        if on_update:
            def progress_callback(data):
                on_update({
                    "progress": data.get("progress", 0.0),
                    "current_results": data.get("current_results", "")
                })
        else:
            progress_callback = None

        # Run the research
        markdown_content, file_path = await deep_research(
            research_task,
            llm,
            agent_state,
            max_search_iterations=max_search_iteration,
            max_query_num=max_query_per_iter,
            use_vision=use_vision,
            headless=headless,
            use_own_browser=use_own_browser,
            chrome_cdp=chrome_cdp,
            progress_callback=progress_callback
        )

        return {
            "markdown_content": markdown_content,
            "file_path": file_path
        }
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        return {
            "markdown_content": f"Error during research: {error_msg}",
            "file_path": None
        }

async def periodic_screenshot_capture(browser_context, agent, on_update, interval=1.0):
    """Periodically capture screenshots and send them to the client"""
    try:
        step = 0
        max_steps = 100  # Default max steps
        
        if agent and hasattr(agent, 'max_steps'):
            max_steps = agent.max_steps
        
        while agent and not getattr(agent, 'stopped', False):
            # Capture screenshot
            encoded_screenshot = await capture_screenshot(browser_context)
            
            # Get current step
            if agent and hasattr(agent, 'state') and hasattr(agent.state, 'step_info'):
                step = getattr(agent.state.step_info, 'step_number', step)
            
            # Calculate progress
            progress = min(step / max_steps, 0.99) if max_steps > 0 else 0.5
            
            # Get model actions and thoughts
            model_actions = ""
            model_thoughts = ""
            if agent and hasattr(agent, 'state') and hasattr(agent.state, 'history'):
                history = agent.state.history
                if history and len(history) > 0:
                    last_item = history[-1]
                    if hasattr(last_item, 'action'):
                        model_actions = str(last_item.action)
                    if hasattr(last_item, 'current_state') and hasattr(last_item.current_state, 'thought'):
                        model_thoughts = last_item.current_state.thought
            
            # Send update to client
            if encoded_screenshot:
                on_update({
                    "screenshot": encoded_screenshot,
                    "progress": progress,
                    "model_actions": model_actions,
                    "model_thoughts": model_thoughts
                })
            
            # Wait for next interval
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        import traceback
        print(f"Error in screenshot capture: {str(e)}")
        print(traceback.format_exc())

async def capture_screenshot(browser_context):
    """Capture a screenshot from the browser context"""
    try:
        # Get the current page
        page = await browser_context.get_current_page()
        
        # Take screenshot
        screenshot_bytes = await page.screenshot(
            type='jpeg',
            quality=75,
            scale="css"
        )
        
        # Encode as base64
        encoded = base64.b64encode(screenshot_bytes).decode('utf-8')
        return encoded
    except Exception as e:
        print(f"Error capturing screenshot: {str(e)}")
        return None

async def cleanup_browser():
    """Clean up browser resources"""
    global _global_browser, _global_browser_context
    
    if _global_browser_context:
        await _global_browser_context.close()
        _global_browser_context = None
    
    if _global_browser:
        await _global_browser.close()
        _global_browser = None 