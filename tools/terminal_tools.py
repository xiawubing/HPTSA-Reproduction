from langchain.tools import tool
import subprocess
import os

ALLOWED_TOOLS = ["ls", "cat", "grep", "curl", "python3", "sqlmap", "mkdir", "echo"]

@tool
def execute_terminal_command(command: str) -> str:
    """
    Execute a terminal command.
    IMPORTANT: 
    1. Commands are stateless. 'cd' will not persist. Use absolute paths or 'cd x && ls'.
    2. Interactive commands will timeout. Use non-interactive flags (e.g., sqlmap --batch).
    """
    try:
        base_cmd = command.strip().split()[0]
        if base_cmd not in ALLOWED_TOOLS and ">" not in command:
             return f"Security Error: Command '{base_cmd}' is not allowed. Allowed: {ALLOWED_TOOLS}"

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.getcwd()
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
            
        if len(output) > 3000:
            output = output[:3000] + "\n...[Output Truncated by System due to length]..."
            
        if result.returncode != 0:
            return f"Command Failed (Exit Code {result.returncode}):\n{output}"
            
        return output

    except subprocess.TimeoutExpired:
        return "Error: Command timed out. Did you forget '--batch' or non-interactive flags?"
    except Exception as e:
        return f"System Error: {str(e)}"