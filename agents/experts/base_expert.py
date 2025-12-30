"""
Base class for expert agents.
Provides common functionality for all task-specific expert agents.
"""

from pyexpat import model
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langgraph.prebuilt import create_react_agent
from ..state import AgentState
from prompts.expert_prompts import get_expert_prompt, BASE_EXPERT_SYSTEM_PROMPT

# Tools
# from tools.browser_tools import navigate_tool, click_tool, fill_form_tool, submit_form_tool, get_current_url, extract_forms
from tools.browser_session import BrowserSession 

from tools.terminal_tools import execute_terminal_command
from tools.file_tools import read_file, write_file, list_directory, generate_valid_image


class BaseExpert:
    """Base class for all expert agents."""
    
    def __init__(self, vulnerability_type: str, specialized_tools: List = None):
        """
        Initialize the expert agent.
        """
        self.vulnerability_type = vulnerability_type
        self.llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
        
        # basic tool
        self.base_tools = [
            execute_terminal_command,
            read_file,
            write_file,
            list_directory,
            generate_valid_image,
        ]
        
        # self.tools = self.base_tools + (specialized_tools or [])
        
        # Prompt
        self.expert_specific_prompt = get_expert_prompt(vulnerability_type)
        self.system_prompt_text = BASE_EXPERT_SYSTEM_PROMPT.format(vulnerability_type=vulnerability_type)
        self.system_prompt_text += "\n\n" + self.expert_specific_prompt
        self.system_prompt_text += """
        CRITICAL INSTRUCTIONS:
        1. **ISOLATED SESSION**: You are running in a fresh browser session. Always start by using 'navigate_tool' to the target URL.
        
        2. **DEPENDENCY HANDLING (CRITICAL)**: 
           - Many forms require specific inputs (e.g., a valid image file) to submit successfully. 
           - If the server checks for image validity (e.g., getimagesize), you **MUST** use the `generate_valid_image` tool to create a real PNG file first.
           - Do NOT upload dummy text files as images; the server will reject them, and your primary attack (XSS/SQLi) will never be saved.
        
        3. **STORED VULNERABILITY VERIFICATION**:
           - For Stored XSS, the injection happens on a "Write" page (e.g., /write-journal.php), but the execution happens on a "Read" page (e.g., /read-journal.php or /index.php).
           - After submitting the payload, you **MUST** navigate to the viewing page to verify if the script executes. Do not assume success just because the form submitted.

        4. **OUTPUT FORMAT**:
           - If you successfully EXPLOIT the vulnerability:
             You MUST provide the full "Reproduction Steps".
             You MUST include the "Payload Used" (content of the malicious input).
             You MUST include the "Exploit URL" (where the shell/script is located or executed).
             End your response with: "STATUS: VULNERABILITY CONFIRMED"
           - If you cannot exploit it after trying all methods:
             End your response with: "STATUS: FAILURE"
        """
        self.system_prompt_text += """
        
        ### GLOBAL NAVIGATION & ERROR HANDLING RULES (CRITICAL):
        1. **BLANK PAGE STRATEGY:** 
           - Vulnerable applications are often poorly coded.
           - If you submit a form and land on a **Blank Page** (White Screen) or get a **500 Error**, DO NOT assume failure.
           - This often means the server processed the request but failed to redirect.
           - **ACTION:** Immediately use `navigate_tool` to manually go to the page where you expect to see the result (e.g., the index, list, or read page).
           
        2. **ISOLATED SESSIONS:**
           - You are in a fresh browser session.
           - You must strictly follow the "Navigate -> Inject -> Verify" loop.
        
        3. **VERIFICATION:**
           - Always verify your attack. Do not trust "success" messages alone.
           - For XSS: Use `check_alerts_tool`.
           - For SQLi/SSTI: Check for data leakage or errors in the HTML.
        """
    
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the expert agent's task.
        """
        # get context
        current_url = state.get("current_url", "No URL set")
        current_plan = state.get("current_plan", "No plan set")
        execution_results = state.get("execution_results", [])
        
        # make current Prompt (User Message)
        task_input = f"""
Current Execution Context:
- Target URL: {current_url}
- Planner's Goal: {current_plan}

Previous Agent Results (Review these to avoid repeating failures):
{self._format_history(execution_results)}

YOUR MISSION:
Analyze the target and attempt to exploit {self.vulnerability_type} vulnerabilities.
1. If you need to see the page source, use 'navigate_tool' or 'get_current_url'.
2. If you find a vulnerability, output specific details.
3. If tools fail, try a different strategy.
"""
        
        # prepare historic message
        # create_react_agent auto manage messages，only put in new 
        input_messages = state.get("messages", []) + [HumanMessage(content=task_input)]

        async with BrowserSession(headless=False) as session:
            browsr_tool = session.get_tools()
            all_tools = browsr_tool + self.base_tools
            agent_runnable = create_react_agent(model=self.llm, tools=all_tools,prompt=self.system_prompt_text)
            try:
                print(f"[*] {self.vulnerability_type}_agent started session on {current_url}")
                result = await agent_runnable.ainvoke({"messages": input_messages})
                output_messages = result["messages"]
                last_msg = output_messages[-1].content
                status = "failure"
                if "STATUS: VULNERABILITY CONFIRMED" in last_msg or "VULNERABILITY CONFIRMED" in last_msg:
                    status = "success"
                final_url = await session._get_url()
                execution_result = {
                    "agent": f"{self.vulnerability_type}_agent",
                    "result": last_msg,
                    "status": status,
                    "url": final_url
                }
                new_messages = output_messages[len(state.get("messages", [])):]
                if not new_messages:
                    new_messages = [AIMessage(content=last_msg)]

                return {
                    "execution_results": [execution_result],
                    "messages": new_messages,
                }

            except Exception as e:
                import traceback
                traceback.print_exc()
                error_msg = f"Error in {self.vulnerability_type}_agent: {str(e)}"
                return {
                    "execution_results": [{
                        "agent": f"{self.vulnerability_type}_agent",
                        "result": error_msg,
                        "status": "error",
                        "url": current_url
                    }],
                    "messages": [AIMessage(content=error_msg)]
                }
    def _format_history(self, results):
        if not results: return "None"
        return "\n".join([f"- {r.get('agent')}: {r.get('status')} - {str(r.get('result'))[:100]}..." for r in results[-3:]])

def create_expert_node(expert: BaseExpert):
    """Factory function for LangGraph node."""
    async def expert_node(state: AgentState) -> Dict[str, Any]:
        return await expert.execute(state)
    return expert_node