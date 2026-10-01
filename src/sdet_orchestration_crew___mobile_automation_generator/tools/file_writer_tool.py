import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class FileWriterInput(BaseModel):
    """Input schema for FileWriterTool."""
    filepath: str = Field(..., description="The relative path where the file should be saved (e.g., 'src/pages/login_page.py')")
    code: str = Field(..., description="The complete, fully formatted Python code to write to the file.")

class FileWriterTool(BaseTool):
    name: str = "Framework File Writer"
    description: str = (
        "Writes Python code directly to the Loco_Mobile_Automation framework and stages it in Git."
    )
    args_schema: Type[BaseModel] = FileWriterInput

    def _run(self, filepath: str, code: str) -> str:
        # 1. Resolve the framework path
        framework_root = os.getenv("FRAMEWORK_ROOT", os.getcwd())
        target_path = os.path.join(framework_root, filepath)
        
        print(f"\n[Tool Execution] Writing and staging code: {target_path}")
        
        # 2. Ensure directories exist
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # 3. Write the file to disk
        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(code)
        except Exception as e:
            return f"Error writing file to disk: {e}"

        # 4. Automatically Stage the file in Git
        try:
            # We run 'git add <filepath>' using the framework_root as the current working directory
            subprocess.run(
                ["git", "add", filepath], 
                cwd=framework_root, 
                check=True,
                capture_output=True
            )
            return f"Success: Code successfully written and staged to Git at {target_path}"
        except subprocess.CalledProcessError as e:
            # If Git fails (e.g., repo isn't initialized), we still report the file was written
            error_msg = e.stderr.decode().strip() if e.stderr else str(e)
            return f"Warning: File written to {target_path}, but failed to stage in Git. Git Error: {error_msg}"