# Module 1 Setup Guide

## Overview
Module 1 provides a complete chat application with authentication, OpenAI Responses API integration, and LangSmith observability.

## Prerequisites

1. **Supabase Account**
   - Sign up at https://supabase.com
   - Create a new project
   - Note your project URL and API keys

2. **OpenAI API Key**
   - Sign up at https://platform.openai.com
   - Create an API key

3. **LangSmith Account**
   - Sign up at https://smith.langchain.com
   - Create a project
   - Get your API key

## Setup Steps

### 1. Database Setup

1. Go to your Supabase Dashboard → SQL Editor
2. Run the migration file: `supabase/migrations/001_initial_schema.sql`
3. Verify tables are created with RLS enabled

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Unix/MacOS:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Create .env file in project root
# Copy from .env.example and fill in your values
```

### 3. Frontend Setup

```bash
cd frontend
npm install

# Create .env file
# Copy from .env.example and fill in your values
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
python backend/main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Test the Application

1. Open http://localhost:5173
2. Sign up with an email and password
3. Create a new chat thread
4. Send a message and see the streaming response
5. Check LangSmith dashboard for traces

## Environment Variables

### Backend (.env in project root)
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENAI_API_KEY=sk-...
LANGSMITH_API_KEY=ls__...
LANGSMITH_PROJECT=agentic-rag-masterclass
```

### Frontend (frontend/.env)
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_API_URL=http://localhost:8000
```

## Architecture

### Backend
- FastAPI server on port 8000
- OpenAI Responses API for managed threads
- LangSmith for tracing
- Supabase for auth and data storage
- SSE for streaming responses

### Frontend
- React + TypeScript + Vite
- Tailwind CSS for styling
- Supabase Auth for authentication
- React Router for navigation
- EventSource for SSE streaming

### Database Schema
- `threads` - Chat threads with OpenAI thread IDs
- `messages` - Message history
- Row-Level Security ensures users only see their own data

## Troubleshooting

**Backend won't start:**
- Check virtual environment is activated
- Verify all environment variables are set
- Check Python version (3.9+)

**Frontend won't start:**
- Check Node version (18+)
- Run `npm install` again
- Clear node_modules and reinstall

**Auth not working:**
- Verify Supabase URL and keys
- Check Supabase Auth is enabled in dashboard
- Confirm email confirmation is disabled (for testing)

**Messages not streaming:**
- Check backend is running
- Verify CORS settings
- Check browser console for errors
- Confirm OpenAI API key is valid

**No traces in LangSmith:**
- Verify LangSmith API key
- Check project name matches
- Ensure environment variables are loaded

## Next Steps

Once Module 1 is working:
1. Test the full flow: signup → login → chat
2. Verify traces appear in LangSmith
3. Check messages are saved in Supabase
4. Review the code to understand the architecture
5. Decide on architectural approach for Module 2 (see PRD.md)
