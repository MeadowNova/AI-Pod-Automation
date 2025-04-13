# planner_agent.py – Planner Agent for Project Planning
import requests

class PlannerAgent:
    def __init__(self, name, ollama_url, model):
        self.name = name
        self.ollama_url = ollama_url
        self.model = model
        self.system_prompt = (
            "You are a Planner Agent focused strictly on completing and organizing a local AI automation project inside VS Code. "
            "Your primary job is to break down Adam's high-level goals into concrete dev tasks to help him finish his print-on-demand automation system. "
            "Only respond with tasks related to project layout, module wiring, backend logic, and developer workflows. Avoid external product launch goals."
        )

    def plan_project_tasks(self, user_goal):
        prompt = f"{self.system_prompt}\n\nUser Goal: {user_goal}\n\nPlannerAgent:"
        try:
            response = requests.post(
                self.ollama_url,
                json={"model": self.model, "prompt": prompt, "stream": False}
            )
            return response.json().get("response", "[No response from Ollama]")
        except Exception as e:
            return f"[PlannerAgent error: {e}]"
