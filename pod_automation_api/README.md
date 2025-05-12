# POD AI Automation API

This is the backend API for the POD AI Automation system, a platform designed to help Etsy POD (Print on Demand) sellers optimize their listings and automate their workflow.

## Features

- Authentication with JWT tokens
- SEO optimization for Etsy listings
- Etsy API integration
- AI-powered content generation

## Getting Started

### Prerequisites

- Python 3.8+
- [Optional] Ollama with qwen3:8b model for AI features

### Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following variables:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
ETSY_CLIENT_ID=your_etsy_client_id
ETSY_CLIENT_SECRET=your_etsy_client_secret
JWT_SECRET=your_jwt_secret
```

### Running the API

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

API documentation will be available at:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## API Contract

The API is defined using OpenAPI 3.1 in the `openapi.yaml` file. This contract is the source of truth for the API and should be updated before making changes to the code.

## Project Structure

```
pod_automation_api/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── auth.py
│   │   │   ├── etsy.py
│   │   │   └── seo.py
│   │   └── api.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── session.py
│   │   └── models.py
│   ├── schemas/
│   │   ├── token.py
│   │   ├── user.py
│   │   ├── etsy.py
│   │   └── seo.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── etsy_service.py
│   │   └── seo_service.py
│   └── main.py
├── openapi.yaml
├── requirements.txt
└── README.md
```

## Development

### Adding New Endpoints

1. Update the `openapi.yaml` file with the new endpoint definition
2. Create or update the corresponding endpoint file in `app/api/endpoints/`
3. Add any necessary schemas in `app/schemas/`
4. Implement the business logic in `app/services/`
5. Update the API router in `app/api/api.py` if needed

### Testing

TODO: Add testing instructions
