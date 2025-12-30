"""
Generic web hacking expert agent.
Provides general web application security testing capabilities.
"""

from .base_expert import BaseExpert, create_expert_node

# Create generic expert instance
generic_expert = BaseExpert(
    vulnerability_type="generic",
    specialized_tools=[]  # Generic agent uses base tools
)

# Create the node function for LangGraph
generic_expert_node = create_expert_node(generic_expert)

