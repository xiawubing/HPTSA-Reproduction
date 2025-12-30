"""
Cross-Site Request Forgery (CSRF) expert agent.
Specialized in identifying and exploiting CSRF vulnerabilities.
"""

from .base_expert import BaseExpert, create_expert_node

# Create CSRF expert instance
csrf_expert = BaseExpert(
    vulnerability_type="csrf",
    specialized_tools=[]  # CSRF agent uses base tools for testing
)

# Create the node function for LangGraph
csrf_expert_node = create_expert_node(csrf_expert)

