# main.py – Custom Agent Loop w/ PlannerAgent + File Tools

import requests
from planner_agent import PlannerAgent
from file_tools import get_folder_structure, read_file, list_directory

# ----- CONFIGURATION -----
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3:latest"

# ----- OLLAMA QUERY WRAPPER -----
def query_ollama(prompt: str, model: str = MODEL_NAME):
    response = requests.post(
        OLLAMA_URL,
        json={"model": model, "prompt": prompt, "stream": False}
    )
    return response.json().get("response", "[No response from Ollama]")

# ----- BASE AGENT CLASS -----
class OllamaAgent:
    def __init__(self, name, role_prompt):
        self.name = name
        self.role_prompt = role_prompt

    def respond(self, message):
        full_prompt = f"{self.role_prompt}\n\nUser: {message}\n\n{self.name}:"
        response = query_ollama(full_prompt)
        return response

# ----- DEFINE AGENTS -----
planner = PlannerAgent(name="PlannerAgent", ollama_url=OLLAMA_URL, model=MODEL_NAME)

agents = [
    OllamaAgent("CoFounder", "You are an AI co-founder helping refine vision, strategy, and direction."),
    OllamaAgent("LeadDeveloper", "You are the lead developer responsible for structuring code, integrating modules, and building utilities in VS Code."),
    OllamaAgent("OperationsExecutor", "You handle execution tasks like file formatting, organization, and automation flow setup."),
    OllamaAgent("GrowthAgent", "You focus on messaging, outreach, marketing copy, and product growth tactics."),
    OllamaAgent("AnalyticsAgent", "You interpret performance data and recommend next steps for improvement.")
]

# ----- CHAT LOOP -----
def main():
    print("\n🎯 PlannerAgent activated. Type a project goal or use commands like 'structure', 'read <file>', or 'list <folder>'. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting.")
            break

        # --- Handle File Tool Commands ---
        if user_input.lower() == "structure":
            print("\n📂 Project Folder Structure:\n")
            print(get_folder_structure(".."))
            continue

        if user_input.lower().startswith("read "):
            filepath = user_input[5:].strip()
            print(f"\n📄 Reading {filepath}...\n")
            print(read_file(filepath))
            continue

        if user_input.lower().startswith("list "):
            folder = user_input[5:].strip()
            print(f"\n📁 Listing contents of {folder}...\n")
            print(list_directory(folder))
            continue

        # --- Planner Agent + Team Chat ---
        print("\n🧠 PlannerAgent says:")
        plan = planner.plan_project_tasks(user_input)
        print(plan)

        for agent in agents:
            print(f"\n🔹 {agent.name} says:")
            reply = agent.respond(user_input)
            print(reply)

if __name__ == "__main__":
    main()
