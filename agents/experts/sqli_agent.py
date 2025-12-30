"""
SQL Injection (SQLi) expert agent.
Specialized in identifying and exploiting SQL injection vulnerabilities.
"""

from .base_expert import BaseExpert, create_expert_node
from tools.sqlmap_wrapper import run_sqlmap

# Create SQLi expert instance with sqlmap tool
sqli_expert = BaseExpert(
    vulnerability_type="sqli",
    specialized_tools=[run_sqlmap]
)

# Create the node function for LangGraph
sqli_expert_node = create_expert_node(sqli_expert)

