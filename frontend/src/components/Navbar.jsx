import React from 'react';
import { Sparkles, Video, FolderKanban, User, LogOut, PlayCircle, RefreshCw } from 'lucide-react';

export default function Navbar({ currentView, setCurrentView, user, onDemoLogin, onOpenProfile, onOpenAuth, onLogout }) {
  const isDemo = user?.email?.includes('rahul.demo');

  return (
    <header className="navbar">
      <div className="nav-brand" onClick={() => setCurrentView('landing')}>
        <div className="nav-logo-icon">
          <Sparkles size={20} />
        </div>
        <div>
          <span style={{ fontWeight: 800, fontSize: '1.05rem' }}>Influencer Help</span>
          <span style={{ display: 'block', fontSize: '0.72rem', color: 'var(--primary-light)', fontWeight: 600, letterSpacing: '0.05em' }}>
            AI CONTENT COPILOT
          </span>
        </div>
      </div>

      <nav className="nav-links">
        {user ? (
          <>
            <button
              className={`nav-btn ${currentView === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentView('dashboard')}
            >
              <Sparkles size={16} />
              <span>Today's Ideas</span>
            </button>

            <button
              className={`nav-btn ${currentView === 'workspace' ? 'active' : ''}`}
              onClick={() => setCurrentView('workspace')}
            >
              <FolderKanban size={16} />
              <span>Workspace</span>
            </button>

            <button
              className={`nav-btn ${currentView === 'profile' ? 'active' : ''}`}
              onClick={onOpenProfile}
            >
              <User size={16} />
              <span>Creator Profile</span>
            </button>
          </>
        ) : (
          <>
            <button className="nav-btn" onClick={() => setCurrentView('landing')}>
              Home
            </button>
            <button className="btn-secondary" style={{ padding: '0.45rem 0.9rem', fontSize: '0.84rem' }} onClick={onDemoLogin}>
              <PlayCircle size={15} color="#f59e0b" />
              <span>Try Rahul Demo</span>
            </button>
            <button className="btn-primary" style={{ padding: '0.45rem 1rem', fontSize: '0.84rem' }} onClick={onOpenAuth}>
              Get Started
            </button>
          </>
        )}
      </nav>

      {user && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          {isDemo ? (
            <span className="badge-demo">Demo Mode (Rahul)</span>
          ) : (
            <div className="nav-user-pill">
              <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{user.display_name}</span>
            </div>
          )}

          {!isDemo && (
            <button
              title="Switch to Rahul Demo"
              onClick={onDemoLogin}
              className="btn-ghost"
              style={{ fontSize: '0.78rem', color: '#f59e0b' }}
            >
              <RefreshCw size={13} />
              <span>Rahul Demo</span>
            </button>
          )}

          <button
            title="Log Out"
            onClick={onLogout}
            className="btn-ghost"
            style={{ padding: '0.45rem' }}
          >
            <LogOut size={16} />
          </button>
        </div>
      )}
    </header>
  );
}
