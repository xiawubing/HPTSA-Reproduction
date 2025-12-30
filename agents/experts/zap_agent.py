"""
OWASP ZAP expert agent.
Specialized in automated vulnerability scanning using OWASP ZAP.
"""

from .base_expert import BaseExpert, create_expert_node
from tools.zap_wrapper import start_zap_scan, get_zap_alerts

# Create ZAP expert instance with ZAP tools
zap_expert = BaseExpert(
    vulnerability_type="zap",
    specialized_tools=[start_zap_scan, get_zap_alerts]
)

# Create the node function for LangGraph
zap_expert_node = create_expert_node(zap_expert)

