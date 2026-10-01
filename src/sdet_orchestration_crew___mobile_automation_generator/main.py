#!/usr/bin/env python
import sys
import os
from sdet_orchestration_crew___mobile_automation_generator.crew import SdetOrchestrationCrewMobileAutomationGeneratorCrew

# This main file is intended to be a way for your to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

# Dynamically resolve the path to the Mobile Automation Repo
# This goes up one level from the Agent repo, then into the Loco Mobile Automation repo
AGENT_REPO_DIR = os.getcwd()
FRAMEWORK_REPO_DIR = os.path.abspath(os.path.join(AGENT_REPO_DIR, "..", "Loco_Mobile_Automation"))

# Set it so the tools can find it
os.environ["FRAMEWORK_ROOT"] = FRAMEWORK_REPO_DIR

def run():
    """
    Run the crew.
    """
    # 1. Read test cases from the test_cases.csv file and framework context from the framework files
    csv_path = "assets/test_cases.csv"
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_content = file.read()
    else:
        print(f"Warning: {csv_path} not found. Using dummy data.")
        csv_content = """Test Case ID,Description,Expected Result
                         TC01,User enters invalid credentials,Error Toast displayed on Login Screen"""

    framework_context_for_pom_generation = load_framework_context_for_pom_generation()
    framework_context_for_test_generation = load_framework_context_for_test_generation()

    # 2. Scan the assets/screens directory dynamically
    assets_dir = "assets/screens"
    available_assets = []
    if os.path.exists(assets_dir):
        available_assets = os.listdir(assets_dir)
    else:
        print(f"Warning: directory '{assets_dir}' not found. Please create it and add your images/xmls.")
        
    assets_string = "\n".join([f"- {f}" for f in available_assets])

    # 3. Pass inputs to the Crew
    inputs = {
        'feature_name': 'Login',
        'module_name': 'login',
        'csv_content': csv_content,
        'framework_context_for_pom_generation': framework_context_for_pom_generation,
        'framework_context_for_test_generation': framework_context_for_test_generation
    }
    
    print(f"\nTarget Framework Directory: {FRAMEWORK_REPO_DIR}")
    print(f"\nSource Assets Directory: {assets_dir}")
    print("Starting Mobile Automation Generator Pipeline...")
    SdetOrchestrationCrewMobileAutomationGeneratorCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'feature_name': 'sample_value'
    }
    try:
        SdetOrchestrationCrewMobileAutomationGeneratorCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        SdetOrchestrationCrewMobileAutomationGeneratorCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'feature_name': 'sample_value'
    }
    try:
        SdetOrchestrationCrewMobileAutomationGeneratorCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def load_framework_context_for_pom_generation() -> str:
    """Reads core base pages and ONE reference POM to inject into the LLM context."""
    # We include base pages and one perfect reference POM to show the LLM how to write POMs
    print("Loading Framework Context for Agent 3...")
    pom_files = [
        "src/pages/base_page.py",
        "src/pages/android_base_page.py",
        "src/pages/ios_base_page.py",
        "src/pages/quiz_poll_page.py"  # One perfect reference POM
    ]
    pom_code = load_file_context(pom_files)
    return pom_code

def load_framework_context_for_test_generation() -> str:
    """Reads conftest.py, ONE refeerence test file and the new POM to give the Synthesizer full context."""
    print("Loading Test Context for Agent 4...")
    files_to_read = [
        "tests/conftest.py",
        "tests/test_quiz_poll.py" # <--- The "Gold Standard" Reference
    ]
    
    test_code = load_file_context(files_to_read)
    return test_code

def load_file_context(relative_file_paths) -> str:
    """Reads framework files from the external Loco_Mobile_Automation repo."""
    context = ""
    for rel_path in relative_file_paths:
        abs_path = os.path.join(FRAMEWORK_REPO_DIR, rel_path)
        if os.path.exists(abs_path):
            with open(abs_path, 'r', encoding='utf-8') as f:
                context += f"\n\n### FILE: {rel_path} ###\n"
                context += f.read()
        else:
            print(f"Context Warning: Could not find {abs_path}")
    return context

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <command> [<args>]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
