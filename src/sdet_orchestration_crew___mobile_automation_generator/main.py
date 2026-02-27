#!/usr/bin/env python
import sys
import os
from sdet_orchestration_crew___mobile_automation_generator.crew import SdetOrchestrationCrewMobileAutomationGeneratorCrew

# This main file is intended to be a way for your to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    # 1. Read CSV
    csv_path = "assets/test_cases.csv" 
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_content = file.read()
    else:
        print(f"Warning: {csv_path} not found. Using dummy data.")
        csv_content = """Test Case ID,Description,Expected Result
                         TC01,User enters invalid credentials,Error Toast displayed on Login Screen"""

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
        'feature_name': 'Quiz & Polls on LiveStream',
        'csv_content': csv_content
    }
    
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
