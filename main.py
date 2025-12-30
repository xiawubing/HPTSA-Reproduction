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

# 2. Add all nodes (这些节点现在都是 async def)
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
        "planner": "planner", # 确保这里包含了 planner 回溯路径
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

# [修改点1] 定义异步 main 函数
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
        # [修改点2] 使用 async for 和 app.astream (异步流)
        async for output in app.astream(initial_state):
            # LangGraph 的 output 通常只有一个 key，但保留循环以防并行扩展
            for key, value in output.items():
                print(f"\n[+] Finished Node: {key}")
                
                if "messages" in value:
                    for msg in value["messages"]:
                        # 1. 如果是 AI 发出的消息（通常包含工具调用）
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            for tool_call in msg.tool_calls:
                                print(f"    [DEBUG-ACTION] 🛠️  Agent wants to call: {tool_call['name']}")
                                print(f"                   Args: {tool_call['args']}")
                        
                        # 2. 如果是工具返回的消息（执行结果）
                        # 注意：LangGraph 有时把 ToolMessage 放在下一轮，但这里通常能看到部分
                        if msg.type == "tool":
                            # 截断过长的输出，防止刷屏
                            content_preview = str(msg.content)[:200] + "..." if len(str(msg.content)) > 200 else str(msg.content)
                            print(f"    [DEBUG-OBSERVATION] 👀 Tool returned: {content_preview}")
                
                
                # Manager 节点的日志逻辑
                if key == "manager" and "next_step" in value:
                    next_step = value['next_step']
                    print(f"    -> Next step: {next_step}")
                    if next_step == "end":
                        # 注意：这里只是标记，真正的停止是循环自然结束
                        # 真正的漏洞判定最好是在 Manager 内部做完
                        pass
                        
                # Expert 节点的日志逻辑
                elif key.endswith("_agent"): # 简化判断逻辑
                    if "execution_results" in value and value["execution_results"]:
                        last_result = value["execution_results"][-1]
                        status = last_result.get('status', 'N/A')
                        print(f"    -> Status: {status}")
                        # 用户要求"全部输出"——输出 execution_results 的全部细节
                        import json
                        print("    -> Full execution result:")
                        try:
                            print(json.dumps(last_result, ensure_ascii=False, indent=2))
                        except Exception:
                            print(str(last_result))
                        # print(f"    -> Result: {str(last_result.get('result', ''))[:200]}...") # 截断长日志
                        
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
    # [修改点3] 使用 asyncio.run 启动事件循环
    # 这是运行异步 Playwright 和异步 LangGraph 的必要条件
    asyncio.run(main())