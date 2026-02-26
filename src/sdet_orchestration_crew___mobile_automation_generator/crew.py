import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
	FileReadTool,
	OCRTool
)


llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.7,
    api_key=os.getenv("GEMINI_API_KEY")
)


@CrewBase
class SdetOrchestrationCrewMobileAutomationGeneratorCrew:
    """SdetOrchestrationCrewMobileAutomationGenerator crew"""

    
    @agent
    def product_owner_and_test_router(self) -> Agent:
        
        return Agent(
            config=self.agents_config["product_owner_and_test_router"],
            tools=[FileReadTool()],
            llm=llm,
        )
    
    @agent
    def multimodal_vision_and_xml_analyzer(self) -> Agent:
        
        return Agent(
            config=self.agents_config["multimodal_vision_and_xml_analyzer"],            
            tools=[OCRTool(), FileReadTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=llm,
        )
    
    @agent
    def page_object_model_pom_crafter(self) -> Agent:
        
        return Agent(
            config=self.agents_config["page_object_model_pom_crafter"],            
            tools=[FileReadTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=llm,
        )
    
    @agent
    def pytest_automation_synthesizer(self) -> Agent:
        
        return Agent(
            config=self.agents_config["pytest_automation_synthesizer"],
            tools=[FileReadTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=llm,
        )
    
    @agent
    def lead_quality_assurance_reviewer(self) -> Agent:
        
        return Agent(
            config=self.agents_config["lead_quality_assurance_reviewer"],            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=llm,
        )
    
    @task
    def parse_test_cases_and_extract_screen_flow(self) -> Task:
        return Task(
            config=self.tasks_config["parse_test_cases_and_extract_screen_flow"],
            markdown=False,
        )
    
    @task
    def analyze_screenshots_and_generate_locators(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_screenshots_and_generate_locators"],
            markdown=False,
        )
    
    @task
    def generate_page_object_model_classes(self) -> Task:
        return Task(
            config=self.tasks_config["generate_page_object_model_classes"],
            markdown=False,
        )
    
    @task
    def write_pytest_test_scripts(self) -> Task:
        return Task(
            config=self.tasks_config["write_pytest_test_scripts"],
            markdown=False,
        )
    
    @task
    def review_and_finalize_code_quality(self) -> Task:
        return Task(
            config=self.tasks_config["review_and_finalize_code_quality"],
            markdown=False,
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the SdetOrchestrationCrewMobileAutomationGenerator crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            chat_llm=llm,
        )


