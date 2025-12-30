"""
Server-Side Template Injection (SSTI) expert agent.
Specialized in identifying and exploiting SSTI vulnerabilities.
"""

from .base_expert import BaseExpert, create_expert_node

# Create SSTI expert instance
ssti_expert = BaseExpert(
    vulnerability_type="ssti",
    specialized_tools=[]  # SSTI agent uses base tools for testing
)

# Create the node function for LangGraph
ssti_expert_node = create_expert_node(ssti_expert)

