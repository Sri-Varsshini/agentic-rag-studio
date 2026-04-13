# Backend Setup

## Prerequisites
- Python 3.9+
- Supabase account
- OpenAI API key
- LangSmith account

## Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file in project root:
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
OPENAI_API_KEY=your_openai_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=agentic-rag-masterclass
```

4. Run the SQL migration in Supabase:
- Go to Supabase Dashboard → SQL Editor
- Run the contents of `supabase/migrations/001_initial_schema.sql`

5. Start the server:
```bash
python backend/main.py
```

Server will run on http://localhost:8000

## API Endpoints

- `GET /health` - Health check
- `POST /api/threads` - Create new thread
- `GET /api/threads` - List user's threads
- `POST /api/threads/{thread_id}/messages` - Send message (SSE streaming)
- `GET /api/threads/{thread_id}/messages` - Get message history
