import asyncio
import sys
from langgraph.graph import StateGraph, END
from agents.state import AgentState
# 确保导入的是 async 版本的节点函数
from agents.planner import planner_node
from agents.manager import manager_node, route_manager
from agents.experts.sqli_agent import sqli_expert_node
from agents.experts.xss_agent import xss_expert_node
from agents.experts.csrf_agent import csrf_expert_node
from agents.experts.ssti_agent import ssti_expert_node
from agents.experts.zap_agent import zap_expert_node
from agents.experts.generic_agent import generic_expert_node

# 1. Initialize the StateGraph
workflow = StateGraph(AgentState)

# 2. Add all nodes async def
workflow.add_node("planner", planner_node)
workflow.add_node("manager", manager_node)
workflow.add_node("sqli_agent", sqli_expert_node)
workflow.add_node("xss_agent", xss_expert_node)
workflow.add_node("csrf_agent", csrf_expert_node)
workflow.add_node("ssti_agent", ssti_expert_node)
workflow.add_node("zap_agent", zap_expert_node)
workflow.add_node("generic_agent", generic_expert_node)

# 3. Define edges
workflow.set_entry_point("planner")
workflow.add_edge("planner", "manager")

workflow.add_conditional_edges(
    "manager",
    route_manager,
    {
        "sqli_agent": "sqli_agent",
        "xss_agent": "xss_agent",
        "csrf_agent": "csrf_agent",
        "ssti_agent": "ssti_agent",
        "zap_agent": "zap_agent",
        "generic_agent": "generic_agent",
        "planner": "planner",
        "end": END
    }
)

# Experts -> Manager
workflow.add_edge("sqli_agent", "manager")
workflow.add_edge("xss_agent", "manager")
workflow.add_edge("csrf_agent", "manager")
workflow.add_edge("ssti_agent", "manager")
workflow.add_edge("zap_agent", "manager")
workflow.add_edge("generic_agent", "manager")

# 4. Compile the workflow
app = workflow.compile()

async def main():
    # Initialize state
    initial_state = {
        "current_url": "http://34.69.38.161:3000/", 
        "messages": [],
        "exploration_history": [],
        "current_plan": "",
        "next_step": "",
        "execution_results": []
    }
    
    print("[*] Starting HPTSA (Hierarchical Planning Team of Security Agents)...")
    print("[*] Architecture: Planner -> Manager -> Expert Agents")
    print("[*] Expert Agents: SQLi, XSS, CSRF, SSTI, ZAP, Generic")
    print(f"[*] Target URL: {initial_state['current_url']}\n")
    
    vulnerability_found = False
    
    try:
        async for output in app.astream(initial_state):
            for key, value in output.items():
                print(f"\n[+] Finished Node: {key}")
                
                if "messages" in value:
                    for msg in value["messages"]:
                        # llm's message
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            for tool_call in msg.tool_calls:
                                print(f"    [DEBUG-ACTION]  Agent wants to call: {tool_call['name']}")
                                print(f"                   Args: {tool_call['args']}")
                        
                        # tool's return message 
                        if msg.type == "tool":
                            content_preview = str(msg.content)[:200] + "..." if len(str(msg.content)) > 200 else str(msg.content)
                            print(f"    [DEBUG-OBSERVATION] 👀 Tool returned: {content_preview}")
                
                
                # Manager node's log
                if key == "manager" and "next_step" in value:
                    next_step = value['next_step']
                    print(f"    -> Next step: {next_step}")
                    if next_step == "end":
                        pass
                        
                # Expert node's log
                elif key.endswith("_agent"):
                    if "execution_results" in value and value["execution_results"]:
                        last_result = value["execution_results"][-1]
                        status = last_result.get('status', 'N/A')
                        print(f"    -> Status: {status}")
                        import json
                        print("    -> Full execution result:")
                        try:
                            print(json.dumps(last_result, ensure_ascii=False, indent=2))
                        except Exception:
                            print(str(last_result))
                        # print(f"    -> Result: {str(last_result.get('result', ''))[:200]}...") 
                        
                        if status == "success":
                            vulnerability_found = True
                            
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n[!] Error during execution: {e}")
    
    # Final summary
    if vulnerability_found:
        print("\n" + "="*60)
        print("[✓] HPTSA execution completed: VULNERABILITY SUCCESSFULLY EXPLOITED!")
        print("="*60)
    else:
        print("\n[*] HPTSA execution completed: No vulnerabilities found.")

if __name__ == "__main__":
    asyncio.run(main())