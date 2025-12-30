from langchain.tools import tool
import subprocess
import os
from pathlib import Path

SQLMAP_PATH = Path(__file__).parent / "sqlmap" / "sqlmap.py"

ALLOWED_ARGS = {
    "dbs", "tables", "columns", "dump",
    "technique", "dbms",
    "level", "risk",
    "threads", "smart", "batch", 
    "tamper", "random-agent"
}

def _run_sqlmap_impl(url: str, data: str = None, cookie: str = None, options: str = None) -> str:
    """
    Run sqlmap to test for SQL injection.
    Output is truncated to prevent context overflow.
    
    Args:
        url: Target URL
        data: POST data (e.g., "id=1&name=test")
        cookie: HTTP Cookie string
        options: Additional options string (e.g., "--level=1 --dbs"). 
                 Only safe options are allowed.
    """
    if not SQLMAP_PATH.exists():
        return f"Error: sqlmap not found at {SQLMAP_PATH}"

    cmd = ["python3", str(SQLMAP_PATH), "-u", url, "--batch"]

    if data:
        cmd.extend(["--data", data])
    if cookie:
        cmd.extend(["--cookie", cookie])

    if options:
        parts = options.strip().split()
        for part in parts:
            clean_arg = part.lstrip("-").split("=")[0]
            if clean_arg in ALLOWED_ARGS:
                cmd.append(part)
            else:
                pass 

    try:
        print(f"[*] Running SQLMap: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=SQLMAP_PATH.parent
        )


        raw_output = result.stdout + result.stderr

        if "connection timed out" in raw_output:
            return "FAILURE: Connection timed out. Target is unreachable."
        if "WAF/IPS identified" in raw_output:
            return "FAILURE: WAF detected! The attack was blocked."
        

        if "Parameter:" in raw_output and "Type:" in raw_output:

            start_index = raw_output.find("Parameter:")
            
            essential_info = raw_output[start_index:]
            
            if len(essential_info) > 2000:
                essential_info = essential_info[:2000] + "\n...[Details Truncated]..."
            
            return f"SUCCESS: SQL Injection Found!\nDetails:\n{essential_info}"

        if "all tested parameters do not appear to be injectable" in raw_output:
            return "RESULT: Scan completed. No SQL injection vulnerability found on this URL/Parameters."

        return f"RESULT: Uncertain outcome.\nLast logs:\n{raw_output[-500:]}"

    except subprocess.TimeoutExpired:
        return "Error: sqlmap timed out (process killed)."
    except Exception as e:
        return f"Error running sqlmap: {str(e)}"

@tool
def run_sqlmap(url: str, data: str = None, cookie: str = None, options: str = None) -> str:
    """
    Run sqlmap to test for SQL injection.
    Output is truncated to prevent context overflow.
    
    Args:
        url: Target URL
        data: POST data (e.g., "id=1&name=test")
        cookie: HTTP Cookie string
        options: Additional options string (e.g., "--level=1 --dbs"). 
                 Only safe options are allowed.
    """
    return _run_sqlmap_impl(url, data, cookie, options)

__all__ = ['run_sqlmap', '_run_sqlmap_impl']