from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Importy Twoich komponentów
from src.llm import local_llm
from src.tools.ebay_tool import EbaySearchTool
from src.tools.local_json_tool import LocalJSONTool
from src.tools.reputation_filter_tool import ReputationFilterTool
import os
from .models.schemas import SourcingResult 
from .tools.Ebay_composite_tool import EbayCompositeTool 
@CrewBase
class EbaySniperCrew:
    """Główna klasa bota"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # --- AGENCI ---
    @agent
    def sourcing_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['sourcing_agent'],
            # Dajemy mu tylko to jedno narzędzie do szukania
            tools=[EbayCompositeTool()], 
            llm=local_llm,
            verbose=True
        )
    
    @agent
    def analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['analyst_agent'],
            llm=local_llm,
            verbose=True
        )

    # --- ZADANIA ---
    @task
    def sourcing_task(self) -> Task:
        return Task(
            config=self.tasks_config['sourcing_task'],
            output_pydantic=SourcingResult
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'],
            context=[self.sourcing_task()]  # Analityk widzi wynik Szperacza
        )

    # --- ZAŁOGA ---
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.sourcing_agent()],
            tasks=[self.sourcing_task()],
            process=Process.sequential,
            verbose=True
        )
