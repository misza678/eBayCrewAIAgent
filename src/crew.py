from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Importy Twoich komponentów
from src.llm import local_llm
from src.tools.ebay_tool import EbaySearchTool

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
            tools=[EbaySearchTool()],
            llm=local_llm,
            verbose=True,
            max_iter=3,
            max_rpm=10
        )

    @agent
    def analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['analyst_agent'],
            llm=local_llm,
            verbose=True
        )

    # --- ZADANIA (Tu podpinamy YAML) ---
    @task
    def sourcing_task(self) -> Task:
        return Task(
            config=self.tasks_config['sourcing_task'],
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'],
            context=[self.sourcing_task()] # <--- Ważne: Analityk widzi wynik Szperacza
        )

    # --- ZAŁOGA ---
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.sourcing_agent(), self.analyst_agent()],
            tasks=[self.sourcing_task(), self.analysis_task()],
            process=Process.sequential,
            verbose=True
        )