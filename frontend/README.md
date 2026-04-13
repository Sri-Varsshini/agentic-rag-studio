# Frontend Setup

## Prerequisites
- Node.js 18+
- Backend server running

## Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create `.env` file:
```
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_URL=http://localhost:8000
```

3. Start development server:
```bash
npm run dev
```

Frontend will run on http://localhost:5173

## Features

- User authentication (signup/login)
- Thread management
- Real-time message streaming
- Responsive chat interface

## Tech Stack

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Supabase Auth
- React Router
