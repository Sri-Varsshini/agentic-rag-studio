# Quick Start - Module 1

## 🚀 Get Running in 5 Minutes

### 1. Set Up Supabase (2 min)
1. Go to https://supabase.com and create a project
2. Go to SQL Editor and run `supabase/migrations/001_initial_schema.sql`
3. Go to Settings → API to get your keys

### 2. Configure Environment (1 min)

Create `.env` in project root:
```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJxxx...
SUPABASE_SERVICE_ROLE_KEY=eyJxxx...
OPENAI_API_KEY=sk-xxx...
LANGSMITH_API_KEY=ls__xxx...
LANGSMITH_PROJECT=agentic-rag-masterclass
```

Create `frontend/.env`:
```bash
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJxxx...
VITE_API_URL=http://localhost:8000
```

### 3. Start Backend (1 min)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r backend/requirements.txt
python backend/main.py
```

### 4. Start Frontend (1 min)
```bash
cd frontend
npm install
npm run dev
```

### 5. Test It! 🎉
1. Open http://localhost:5173
2. Sign up with any email/password
3. Create a chat and send a message
4. Watch it stream!

## ✅ What You Built

- ✅ Full auth system with Supabase
- ✅ Chat UI with thread management
- ✅ OpenAI Responses API integration
- ✅ Streaming responses via SSE
- ✅ LangSmith tracing
- ✅ Row-Level Security

## 🐛 Common Issues

**"Module not found" error:**
```bash
pip install pydantic-settings
```

**Frontend won't connect:**
- Check backend is running on port 8000
- Verify VITE_API_URL in frontend/.env

**Auth fails:**
- Disable email confirmation in Supabase → Auth → Settings
- Check your Supabase keys are correct

**No streaming:**
- Verify OpenAI API key is valid
- Check browser console for errors

## 📚 Next Steps

1. Review the code to understand the architecture
2. Check LangSmith for traces
3. Look at Supabase tables to see stored data
4. Read PRD.md to decide on Module 2 approach
5. Ready for Module 2? Let's build custom RAG!
