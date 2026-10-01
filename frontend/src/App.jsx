import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import BriefStudio from './components/BriefStudio';
import WorkspaceView from './components/WorkspaceView';
import OnboardingModal from './components/OnboardingModal';
import IdeaDetailModal from './components/IdeaDetailModal';
import FeedbackModal from './components/FeedbackModal';
import AuthModal from './components/AuthModal';
import ProfileModal from './components/ProfileModal';
import { api, getAuthToken, setAuthToken, removeAuthToken } from './api';

export default function App() {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [currentView, setCurrentView] = useState('landing'); // 'landing', 'dashboard', 'brief_studio', 'workspace'
  const [loadingApp, setLoadingApp] = useState(true);

  // Active brief for studio
  const [activeBrief, setActiveBrief] = useState(null);

  // Active idea for detail modal
  const [activeIdeaForDetail, setActiveIdeaForDetail] = useState(null);

  // Modals state
  const [isOnboardingOpen, setIsOnboardingOpen] = useState(false);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [feedbackConfig, setFeedbackConfig] = useState({ isOpen: false, ideaId: null, briefId: null, rating: 'useful' });

  // Initial user fetch
  useEffect(() => {
    const initAuth = async () => {
      const token = getAuthToken();
      if (token) {
        try {
          const userData = await api.getMe();
          setUser(userData);
          const profileData = await api.getProfile();
          setProfile(profileData);
          setCurrentView('dashboard');
        } catch (err) {
          console.warn('Session expired or invalid token:', err);
          removeAuthToken();
          setUser(null);
          setCurrentView('landing');
        }
      } else {
        setCurrentView('landing');
      }
      setLoadingApp(false);
    };
    initAuth();
  }, []);

  const handleDemoLogin = async () => {
    try {
      setLoadingApp(true);
      const res = await api.loginDemo();
      setAuthToken(res.access_token);
      setUser(res.user);
      const profileData = await api.getProfile();
      setProfile(profileData);
      setCurrentView('dashboard');
    } catch (err) {
      alert(err.message || 'Demo login failed');
    } finally {
      setLoadingApp(false);
    }
  };

  const handleLogout = () => {
    removeAuthToken();
    setUser(null);
    setProfile(null);
    setActiveBrief(null);
    setCurrentView('landing');
  };

  const handleStartCreating = () => {
    if (!user) {
      setIsAuthOpen(true);
    } else {
      setIsOnboardingOpen(true);
    }
  };

  const handleGenerateBrief = async (idea) => {
    try {
      setLoadingApp(true);
      const brief = await api.generateBrief({
        idea_id: idea.id,
        creator_notes: 'Focus on beginner friendly cues and relatable language'
      });
      setActiveBrief(brief);
      setCurrentView('brief_studio');
    } catch (err) {
      alert(err.message || 'Error generating brief');
    } finally {
      setLoadingApp(false);
    }
  };

  const handleSelectBriefFromWorkspace = (brief) => {
    setActiveBrief(brief);
    setCurrentView('brief_studio');
  };

  const handleOpenFeedback = (ideaId, briefId, rating = 'useful') => {
    setFeedbackConfig({
      isOpen: true,
      ideaId,
      briefId,
      rating
    });
  };

  if (loadingApp) {
    return (
      <div className="app-viewport" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="pulse" style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary-light)', marginBottom: '0.5rem' }}>
            Influencer Help — AI Content Copilot
          </div>
          <p style={{ color: 'var(--text-subtle)', fontSize: '0.9rem' }}>Loading creator studio...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-viewport">
      <Navbar
        currentView={currentView}
        setCurrentView={setCurrentView}
        user={user}
        onDemoLogin={handleDemoLogin}
        onOpenProfile={() => setIsProfileOpen(true)}
        onOpenAuth={() => setIsAuthOpen(true)}
        onLogout={handleLogout}
      />

      <main style={{ flex: 1 }}>
        {currentView === 'landing' && (
          <LandingPage
            onStartCreating={handleStartCreating}
            onDemoLogin={handleDemoLogin}
            onOpenAuth={() => setIsAuthOpen(true)}
          />
        )}

        {currentView === 'dashboard' && (
          <Dashboard
            profile={profile}
            onOpenProfile={() => setIsProfileOpen(true)}
            onSelectIdeaForDetail={(idea) => setActiveIdeaForDetail(idea)}
            onGenerateBriefForIdea={handleGenerateBrief}
            onOpenFeedback={handleOpenFeedback}
          />
        )}

        {currentView === 'brief_studio' && activeBrief && (
          <BriefStudio
            brief={activeBrief}
            onBack={() => setCurrentView('dashboard')}
            onSaveBriefSuccess={(saved) => setActiveBrief(saved)}
            onRegenerate={() => handleGenerateBrief({ id: activeBrief.idea_id })}
            onOpenFeedback={handleOpenFeedback}
          />
        )}

        {currentView === 'workspace' && (
          <WorkspaceView
            onSelectBrief={handleSelectBriefFromWorkspace}
            onSelectIdeaForDetail={(idea) => setActiveIdeaForDetail(idea)}
          />
        )}
      </main>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--border-subtle)', padding: '2rem 1.5rem', textAlign: 'center', fontSize: '0.84rem', color: 'var(--text-subtle)', marginTop: 'auto' }}>
        <p style={{ marginBottom: '0.35rem' }}>
          <strong>Influencer Help — AI Content Copilot</strong> • Turn niche, audience & gear into concrete shootable content.
        </p>
        <p style={{ fontSize: '0.78rem' }}>
          Content briefs and estimates are planning tools. No automatic publishing or guaranteed metrics.
        </p>
      </footer>

      {/* Modals */}
      <OnboardingModal
        isOpen={isOnboardingOpen}
        onClose={() => setIsOnboardingOpen(false)}
        currentProfile={profile}
        onProfileSaved={(newProfile) => {
          setProfile(newProfile);
          setCurrentView('dashboard');
        }}
      />

      <IdeaDetailModal
        isOpen={!!activeIdeaForDetail}
        onClose={() => setActiveIdeaForDetail(null)}
        idea={activeIdeaForDetail}
        onCreateMyReel={handleGenerateBrief}
      />

      <FeedbackModal
        isOpen={feedbackConfig.isOpen}
        onClose={() => setFeedbackConfig(prev => ({ ...prev, isOpen: false }))}
        ideaId={feedbackConfig.ideaId}
        briefId={feedbackConfig.briefId}
        initialRating={feedbackConfig.rating}
      />

      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onAuthSuccess={async (newUser) => {
          setUser(newUser);
          const p = await api.getProfile();
          setProfile(p);
          setCurrentView('dashboard');
        }}
        onDemoLogin={handleDemoLogin}
      />

      <ProfileModal
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
        profile={profile}
        onProfileUpdated={(updated) => setProfile(updated)}
      />
    </div>
  );
}
