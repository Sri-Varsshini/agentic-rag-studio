import { NavLink } from 'react-router-dom'
import { supabase } from '../lib/supabase'

export default function Nav() {
  return (
    <nav className="h-12 bg-white border-b flex items-center justify-between px-4">
      <div className="flex gap-4">
        <NavLink
          to="/chat"
          className={({ isActive }) => `text-sm font-medium ${isActive ? 'text-blue-600' : 'text-gray-600 hover:text-gray-900'}`}
        >
          Chat
        </NavLink>
        <NavLink
          to="/documents"
          className={({ isActive }) => `text-sm font-medium ${isActive ? 'text-blue-600' : 'text-gray-600 hover:text-gray-900'}`}
        >
          Documents
        </NavLink>
      </div>
      <button
        onClick={() => supabase.auth.signOut()}
        className="text-sm text-gray-500 hover:text-gray-700"
      >
        Logout
      </button>
    </nav>
  )
}
