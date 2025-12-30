from langchain.tools import tool
import os
from pathlib import Path

MAX_READ_LENGTH = 5000

CURRENT_FILE = Path(__file__).resolve()

PROJECT_ROOT = CURRENT_FILE.parent.parent

WORKSPACE_PATH = os.path.join(PROJECT_ROOT, "agent_workspace")

print(f"[Config] Agent Workspace set to: {WORKSPACE_PATH}")

os.makedirs(WORKSPACE_PATH, exist_ok=True)

def _is_safe_path(path: str) -> bool:
    absolute_path = os.path.abspath(os.path.join(WORKSPACE_PATH, path))
    return absolute_path.startswith(WORKSPACE_PATH)

@tool
def list_directory(directory_path: str = ".") -> str:
    """
    List files in a directory with type indicators.
    Use this to see what files are created.
    """
    if not _is_safe_path(directory_path):
        return "Security Error: You can only access files inside the workspace."

    try:
        full_path = os.path.join(WORKSPACE_PATH, directory_path)
        items = os.listdir(full_path)
        output = []
        for item in items:
            item_path = os.path.join(full_path, item)
            if os.path.isdir(item_path):
                output.append(f"[DIR]  {item}")
            else:
                output.append(f"[FILE] {item}")
        return "\n".join(output) if output else "(Directory is empty)"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def read_file(file_path: str) -> str:
    """
    Read the contents of a text file.
    Output is truncated to 5000 characters to save context.
    """
    if not _is_safe_path(file_path):
        return "Security Error: Access denied. Stay in your workspace."

    try:
        full_path = os.path.join(WORKSPACE_PATH, file_path)
        if not os.path.exists(full_path):
            return "Error: File not found."
            
        with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read(MAX_READ_LENGTH + 100)
            
        if len(content) > MAX_READ_LENGTH:
            return content[:MAX_READ_LENGTH] + "\n\n...[Content Truncated]..."
        return content
    except Exception as e:
        return f"Error reading file (is it binary?): {str(e)}"

@tool
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file in the workspace.
    Useful for creating Python scripts or saving notes.
    """
    if not _is_safe_path(file_path):
        return "Security Error: Access denied. Stay in your workspace."

    try:
        full_path = os.path.join(WORKSPACE_PATH, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@tool
def create_webshell(filename: str = "shell.php"):
    """Creates a simple PHP webshell for testing RCE."""
    content = "<?php echo 'HACKED_SUCCESS_' . 12345; ?>"
    with open(filename, "w") as f:
        f.write(content)
    return f"Created {filename} with simple echo payload."

@tool
def generate_valid_image(filename: str = "test_image.png"):
    """
    Generates a valid, minimal PNG image file. 
    Use this when a form requires a valid image upload (to bypass getimagesize checks) 
    while you are testing other vulnerabilities like XSS or SQLi.
    """
    minimal_png = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
        b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    
    try:
        file_path = os.path.abspath(os.path.join(os.getcwd(), filename))
        with open(file_path, "wb") as f:
            f.write(minimal_png)
        return f"Successfully generated valid PNG image at: {file_path}"
    except Exception as e:
        return f"Error generating image: {str(e)}"