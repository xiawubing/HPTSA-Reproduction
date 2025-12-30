"""
Wrapper for OWASP ZAP tool integration.
ZAP agent has access to ZAP for automated vulnerability scanning.
"""

from langchain.tools import tool
import subprocess
import time
import requests

# ZAP API configuration
ZAP_API_URL = "http://localhost:8080"  # Default ZAP API URL

@tool
def start_zap_scan(url: str, scan_type: str = "spider") -> str:
    """
    Start a ZAP scan on the target URL.
    
    Args:
        url: Target URL to scan
        scan_type: Type of scan - "spider" (crawl) or "active" (active scan)
        
    Returns:
        Scan results or error message
    """
    try:
        if scan_type == "spider":
            # Start spider scan
            response = requests.get(
                f"{ZAP_API_URL}/JSON/spider/action/scan/",
                params={"url": url}
            )
            scan_id = response.json().get("scan")
            
            # Wait for scan to complete
            while True:
                status_response = requests.get(
                    f"{ZAP_API_URL}/JSON/spider/view/status/",
                    params={"scanId": scan_id}
                )
                status = status_response.json().get("status")
                if int(status) >= 100:
                    break
                time.sleep(2)
            
            # Get results
            results_response = requests.get(
                f"{ZAP_API_URL}/JSON/spider/view/results/",
                params={"scanId": scan_id}
            )
            return f"ZAP spider scan completed:\n{results_response.json()}"
            
        elif scan_type == "active":
            # Start active scan
            response = requests.get(
                f"{ZAP_API_URL}/JSON/ascan/action/scan/",
                params={"url": url}
            )
            scan_id = response.json().get("scan")
            
            # Wait for scan to complete
            while True:
                status_response = requests.get(
                    f"{ZAP_API_URL}/JSON/ascan/view/status/",
                    params={"scanId": scan_id}
                )
                status = status_response.json().get("status")
                if int(status) >= 100:
                    break
                time.sleep(5)
            
            # Get alerts
            alerts_response = requests.get(f"{ZAP_API_URL}/JSON/core/view/alerts/")
            return f"ZAP active scan completed:\n{alerts_response.json()}"
        else:
            return f"Error: Unknown scan type: {scan_type}"
            
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to ZAP API. Make sure ZAP is running on localhost:8080"
    except Exception as e:
        return f"Error running ZAP scan: {str(e)}"

@tool
def get_zap_alerts(url: str = None) -> str:
    """
    Get ZAP security alerts for a specific URL or all URLs.
    
    Args:
        url: Optional URL to filter alerts
        
    Returns:
        JSON string of alerts
    """
    try:
        if url:
            response = requests.get(
                f"{ZAP_API_URL}/JSON/core/view/alerts/",
                params={"baseurl": url}
            )
        else:
            response = requests.get(f"{ZAP_API_URL}/JSON/core/view/alerts/")
        
        return f"ZAP alerts:\n{response.json()}"
    except Exception as e:
        return f"Error getting ZAP alerts: {str(e)}"

