from dotenv import load_dotenv
load_dotenv() 
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.messages import HumanMessage
from langchain_core.messages import HumanMessage, SystemMessage 

from .state import AgentState
from prompts.manager_prompt import MANAGER_SYSTEM_PROMPT, MANAGER_USER_TEMPLATE
import json
import re

llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)

async def manager_node(state: AgentState):
    
    current_plan = state.get("current_plan", "")
    current_url = state.get("current_url", "")
    execution_results = state.get("execution_results", [])
    
    # Format execution results
    if execution_results:
        last_result = execution_results[-1]
        if last_result.get("status")=="success":
            print(f"\n[Manager] Vulnerability Found by {last_result.get('agent')}!")
            print(f"          Exploit Proof: {str(last_result.get('result'))[:100]}...")
            return {
                "next_step": "end",
                "messages": [HumanMessage(content="Vulnerability confirmed. Mission accomplished.")]
            }

    results_str = "No previous executions"
    if execution_results:
        results_list = []
        for item in execution_results[-5:]:
            res_text = str(item.get('result', '')).replace("{", "{{").replace("}", "}}")[:500]
            results_list.append(
                f"Agent: {item.get('agent')}\nStatus: {item.get('status')}\nResult: {res_text}\n"
            )
        results_str = "\n".join(results_list)

    # make Prompt
    user_prompt = MANAGER_USER_TEMPLATE.format(
        current_plan=str(current_plan).replace("{", "{{").replace("}", "}}"),
        current_url=str(current_url).replace("{", "{{").replace("}", "}}"),
        execution_results=results_str
    )    

    json_instruction = """
\nINSTRUCTION:
Respond ONLY with a JSON object. No Markdown.
Format: {"next_step": "AGENT_NAME", "reasoning": "brief explanation"}
Valid Agents: sqli_agent, xss_agent, csrf_agent, ssti_agent, zap_agent, generic_agent, planner, end.

DECISION LOGIC:
1. If the last agent FAILED (status: failure), decide:
   - Try a different agent? (e.g. SQLi failed -> try XSS)
   - If ALL ideas failed, route to 'planner' to create a new plan.
2. If you found a vulnerability, route to 'end'.
"""

    messages = [
        SystemMessage(content=MANAGER_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt + json_instruction)
    ]
    
    response = await llm.ainvoke(messages)
    
    content = response.content.strip()
    content = re.sub(r"^```json|^```", "", content).strip()
    content = re.sub(r"```$", "", content).strip()

    next_step = "generic_agent"
    
    try:
        data = json.loads(content)
        intent = data.get("next_step", "").lower()
        
        valid_steps = {
            "sqli_agent", "xss_agent", "csrf_agent", "ssti_agent", 
            "zap_agent", "generic_agent", "planner", "end"
        }
        
        # 归一化 (sqli -> sqli_agent)
        if intent in valid_steps:
            next_step = intent
        elif f"{intent}_agent" in valid_steps:
            next_step = f"{intent}_agent"
            
    except json.JSONDecodeError:
        print(f"[Manager] Warning: LLM output invalid JSON: {content[:50]}...")
        if "planner" in content.lower(): next_step = "planner"
        elif "end" in content.lower(): next_step = "end"
        

    is_success = any(r.get("status") == "success" for r in execution_results)
    
    if next_step == "end" and not is_success:
        print("[Manager] LLM tried to give up. Forcing RE-PLANNING.")
        next_step = "planner"

    target_url = current_url
    static_extensions = r"\.(jpg|jpeg|png|gif|bmp|svg|webp|css|js|woff|woff2|ttf|ico)$"

    # check URL's end
    is_static_resource = re.search(static_extensions, current_url, re.IGNORECASE)
    
    # check if URL has upload category feature
    is_upload_path = "/uploads/" in current_url or "/media/" in current_url or "/static/" in current_url

    if is_static_resource or is_upload_path:
        print(f"[Manager] Detected static/dead-end URL: {current_url}")
        
        # exploration_history[0] is planner's initial page
        history = state.get("exploration_history", [])
        
        if history and len(history) > 0:
            # find entry page
            original_url = history[0].get("url")
            
            # when URL not null and bad URL, roll back
            if original_url and original_url != current_url:
                print(f"[Manager] Auto-Correcting URL (Back to Start): {current_url} -> {original_url}")
                target_url = original_url
        else:
            print(f"[Manager] Warning: No history found to revert to. Agent might be stuck on {current_url}")

    return {
        "next_step": next_step,
        "messages": [response],
        "current_url": target_url,
    }

def route_manager(state: AgentState):
    return state.get("next_step", "generic_agent")
