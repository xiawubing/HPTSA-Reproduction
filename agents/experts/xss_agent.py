"""
Cross-Site Scripting (XSS) expert agent.
Specialized in identifying and exploiting XSS vulnerabilities.
"""

from .base_expert import BaseExpert, create_expert_node

# Create XSS expert instance
xss_expert = BaseExpert(
    vulnerability_type="xss",
    specialized_tools=[]  # XSS agent uses base tools for manual testing
)

# Create the node function for LangGraph
xss_expert_node = create_expert_node(xss_expert)

