from dotenv import load_dotenv
load_dotenv() 
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from .state import AgentState
# from tools.browser_tools import navigate_tool, click_tool, extract_forms, get_current_url
from tools.browser_session import BrowserSession
from prompts.planner_prompt import PLANNER_SYSTEM_PROMPT

llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)

async def planner_node(state: AgentState):
    """
    Hierarchical Planner node:
    1. Explores the environment (website) using tools autonomously
    2. Analyzes HTML structure by navigating and clicking links
    3. Identifies potential attack surfaces
    4. Generates high-level instructions for the Manager
    """
    current_url = state.get("current_url", "")
    exploration_history = state.get("exploration_history", [])
    execution_results = state.get("execution_results", [])
    
    # Format exploration history
    history_str = "\n".join([
        f"- {item.get('url', 'Unknown')}: {item.get('discovered', 'N/A')}"
        for item in exploration_history[-5:]
    ]) if exploration_history else "None"
    
    # Format execution results
    results_str = "\n".join([
        f"- {item.get('agent', 'Unknown')}: {item.get('status', 'N/A')} - {item.get('result', '')[:100]}"
        for item in execution_results[-5:]
    ]) if execution_results else "None"
    
    # Build task input for planner agent
    task_input = f"""
Current Target URL: {current_url}

Exploration History:
{history_str}

Previous Execution Results:
{results_str}

YOUR MISSION:
1. Explore the website starting from the target URL using navigate_tool
2. Use click_tool to explore links and discover more pages
3. Use extract_forms to identify all forms and input fields
4. Use get_current_url to track where you are
5. Analyze the website structure and identify potential attack surfaces
6. Generate a high-level plan for the Team Manager

IMPORTANT:
- You can navigate to multiple pages to get a comprehensive understanding
- Click on interesting links (forms, user inputs, search functions, etc.)
- Extract forms from each page you visit
- After thorough exploration, provide your analysis and plan
- Do NOT execute attacks - only identify potential vulnerabilities
"""
    
    input_messages = state.get("messages", []) + [HumanMessage(content=task_input)]

    async with BrowserSession(headless=True) as session:
        planner_tools = session.get_tools()
        
        agent_executor = create_react_agent(
            model=llm,
            tools=planner_tools,
            prompt=PLANNER_SYSTEM_PROMPT
        )
        
        try:
            # result = agent_executor.invoke({"messages": input_messages})
            result = await agent_executor.ainvoke({"messages": input_messages})
            
            print("==== PLANNER RAW OUTPUT ====")
            for msg in result["messages"]:
                print(f"{msg.type.upper()}: {msg.content}\n")
            print("==== END PLANNER OUTPUT ====")
            
            last_message = result["messages"][-1]
            plan_content = last_message.content
            
            final_url = await session._get_url() 
            
            # renew exploration_history
            exploration_history = state.get("exploration_history", [])
            new_history_entry = {
                "url": final_url,
                "plan": plan_content
            }
            exploration_history.append(new_history_entry)

            # only keep new message's part
            new_messages = result["messages"][len(state.get("messages", [])):]
            if not new_messages:
                new_messages = [last_message]

            return {
                "current_plan": plan_content,
                "messages": result["messages"],
                "current_url": final_url
            }
            
        except Exception as e:
            print(f"\n[!!!] Planner 发生异常: {e}") 
            return {"current_plan": f"Planner Error: {str(e)}"}