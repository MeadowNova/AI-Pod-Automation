# Project Directory Structure
project_root/
├── autogen_agents_core/          # Agent framework
│   ├── agents/                   # Agent implementations
│   │   ├── co_founder/
│   │   ├── lead_developer/
│   │   ├── planner/
│   │   ├── strategist/
│   │   └── assistant/
│   ├── framework/                # Core framework components
│   │   ├── agent_base.py
│   │   ├── memory.py
│   │   ├── messaging.py
│   │   ├── orchestrator.py
│   │   ├── prompt_chain.py
│   │   └── multimodal_integration.py
│   ├── services/                 # Service implementations
│   │   └── learning_service.py
│   └── utils/                    # Utility functions
│       ├── file_tools.py
│       └── logging_config.py
│
├── pod_automation/               # POD automation modules
│   ├── workers/                  # Worker implementations
│   │   ├── design_generation.py
│   │   ├── mockup_generator.py
│   │   ├── prompt_optimizer.py
│   │   ├── seo_optimizer.py
│   │   ├── publishing_agent.py
│   │   ├── stable_diffusion.py
│   │   └── trend_forecaster.py
│   ├── api/                      # API clients
│   │   ├── printify_api.py
│   │   ├── etsy_api.py
│   │   ├── pinterest_api.py
│   │   └── stable_diffusion_api.py
│   ├── config/                   # Configuration
│   │   ├── logging_config.py
│   │   ├── api_config.py
│   │   └── worker_config.py
│   ├── data/                     # Data storage
│   │   ├── designs/
│   │   ├── mockups/
│   │   ├── templates/
│   │   ├── trends/
│   │   ├── memory/
│   │   └── tasks/
│   ├── shared/                   # Shared utilities
│   │   ├── utils.py
│   │   └── constants.py
│   └── workers_service.py        # Workers service API
│
├── docker/                       # Docker configuration
│   ├── Dockerfile.agents
│   ├── Dockerfile.workers
│   └── Dockerfile.ollama
│
├── tests/                        # Test suite
│   ├── test_agents.py
│   ├── test_workers.py
│   └── test_integration.py
│
├── main.py                       # Main entry point
├── docker-compose.yml            # Docker compose config
├── .env.example                  # Environment variables template
├── requirements.txt              # Dependencies
└── README.md                     # Documentation