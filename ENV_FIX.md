# IMPORTANT: .env File Setup

## The Issue
You have frontend variables (VITE_*) in the backend .env file. They need to be separated.

## Solution: Create TWO .env files

### 1. Backend .env
**Location:** `<project-root>/.env`

**Content (NO VITE_ prefix):**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
OPENAI_API_KEY=your_openai_key_here
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT=agentic-rag-masterclass
```

### 2. Frontend .env
**Location:** `<project-root>/frontend/.env`

**Content (WITH VITE_ prefix):**
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key_here
VITE_API_URL=http://localhost:8000
```

## Quick Fix Steps

1. **Check your current .env file location**
   - If it's in the project root, remove all VITE_* variables
   - Keep only the backend variables (without VITE_ prefix)

2. **Create frontend/.env**
   - Create a new file: `frontend\.env`
   - Add only the VITE_* variables

3. **Restart both servers**
   - Stop backend (Ctrl+C)
   - Stop frontend (Ctrl+C)
   - Start backend: `python backend/main.py`
   - Start frontend: `cd frontend && npm run dev`

## Example

**WRONG ❌ (mixing in one file):**
```
SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_URL=https://your-project.supabase.co  # This causes the error!
```

**CORRECT ✅ (two separate files):**

**Root .env:**
```
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
```

**frontend/.env:**
```
VITE_SUPABASE_URL=https://...
VITE_SUPABASE_ANON_KEY=...
```

## Why This Happens

- Backend uses `pydantic-settings` which reads `.env` from project root
- It expects ONLY the fields defined in `backend/config.py`
- Frontend uses Vite which reads `.env` from `frontend/` folder
- Vite requires `VITE_` prefix for environment variables

## After Fixing

Your backend should start without errors and you'll see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```
