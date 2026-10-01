import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# --- DIRECTORY SCANNER TOOL ---
class ListDirectoryInput(BaseModel):
    directory_path: str = Field(..., description="Relative path to directory, e.g., 'src/utils' or 'src/pages'")

class ListDirectoryTool(BaseTool):
    name: str = "List Directory Contents"
    description: str = (
        "Lists all files inside a given directory in the framework. "
        "Use this to explore what utility files or page objects are available."
    )
    args_schema: Type[BaseModel] = ListDirectoryInput

    def _run(self, directory_path: str) -> str:
        # Get the framework root from environment variables
        framework_root = os.getenv("FRAMEWORK_ROOT", os.getcwd())
        target_path = os.path.join(framework_root, directory_path)
        
        if not os.path.exists(target_path):
            return f"Directory not found: {directory_path}"
        try:
            files = [f for f in os.listdir(target_path) if f.endswith('.py') and not f.startswith('__')]
            return f"Files in '{directory_path}':\n" + "\n".join(files)
        except Exception as e:
            return f"Error reading directory: {e}"

# --- Read Framework File Tool ---
class ReadFrameworkFileInput(BaseModel):
    file_path: str = Field(..., description="Relative path to file, e.g., 'src/utils/test_utils.py' or 'src/pages/login_page.py'")

class ReadFrameworkFileTool(BaseTool):
    name: str = "Read Framework File"
    description: str = (
        "Reads the complete content of a specific python file in the framework. "
        "Use this to read existing config files, Page Objects (to modify them) or Utility functions (to learn how to use them) or Test files (to modify them)."
    )
    args_schema: Type[BaseModel] = ReadFrameworkFileInput

    def _run(self, file_path: str) -> str:
        # Get the framework root from environment variables
        framework_root = os.getenv("FRAMEWORK_ROOT", os.getcwd())
        target_path = os.path.join(framework_root, file_path)
        
        if not os.path.exists(target_path):
            return f"FILE DOES NOT EXIST: {file_path}. You will need to create it from scratch."
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"