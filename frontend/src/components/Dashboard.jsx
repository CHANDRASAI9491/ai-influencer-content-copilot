import React, { useState, useEffect } from 'react';
import { Sparkles, Video, Clock, ShieldAlert, CheckCircle, ThumbsUp, ThumbsDown, SlidersHorizontal, ArrowRight, RefreshCw, Smartphone, MapPin, Eye } from 'lucide-react';
import { api } from '../api';

export default function Dashboard({
  profile,
  onOpenProfile,
  onSelectIdeaForDetail,
  onGenerateBriefForIdea,
  onOpenFeedback
}) {
  const [ideas, setIdeas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  // Request override state
  const [overrideGoal, setOverrideGoal] = useState('');
  const [overrideTime, setOverrideTime] = useState('');
  const [overrideEnv, setOverrideEnv] = useState('');
  const [additionalNotes, setAdditionalNotes] = useState('');

  const fetchExistingIdeas = async () => {
    try {
      setInitialLoading(true);
      const data = await api.listIdeas();
      if (data && data.length > 0) {
        setIdeas(data.slice(0, 5));
      } else {
        // Automatically generate initial 5 ideas if none exist
        await handleGenerateIdeas();
      }
    } catch (err) {
      console.error('Fetch ideas error:', err);
    } finally {
      setInitialLoading(false);
    }
  };

  useEffect(() => {
    fetchExistingIdeas();
  }, []);

  const handleGenerateIdeas = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const payload = {
        goal: overrideGoal.trim() || undefined,
        available_time: overrideTime.trim() || undefined,
        environment: overrideEnv.trim() || undefined,
        additional_notes: additionalNotes.trim() || undefined,
      };
      const newIdeas = await api.generateIdeas(payload);
      setIdeas(newIdeas);
      setShowFilters(false);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to generate ideas. Please retry.');
    } finally {
      setLoading(false);
      setInitialLoading(false);
    }
  };

  const getDifficultyBadge = (diff) => {
    const d = (diff || 'Easy').toLowerCase();
    if (d.includes('easy')) return 'badge-emerald';
    if (d.includes('medium')) return 'badge-amber';
    return 'badge-coral';
  };

  return (
    <div className="container" style={{ paddingTop: '2.5rem', paddingBottom: '4rem' }}>
      {/* Header Section (Section 5 requirements) */}
      <div style={{ textAlign: 'center', maxWidth: '760px', margin: '0 auto 2.5rem' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.45rem', padding: '0.3rem 0.85rem', background: 'rgba(139, 92, 246, 0.12)', border: '1px solid rgba(139, 92, 246, 0.28)', borderRadius: 'var(--radius-full)', marginBottom: '1rem' }}>
          <Sparkles size={14} color="var(--primary-light)" />
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary-light)' }}>
            Personalized Content Engine
          </span>
        </div>

        <h1 style={{ fontSize: '2.6rem', lineHeight: 1.2, marginBottom: '0.75rem' }}>
          What do you want to create today?
        </h1>

        <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', lineHeight: 1.5, marginBottom: '1.75rem' }}>
          Get personalized content ideas based on your niche, audience, goals, time, and resources.
        </p>

        {/* Creator Context Banner */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexWrap: 'wrap',
          gap: '0.65rem',
          background: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '0.75rem 1.2rem',
          marginBottom: '1.75rem',
          fontSize: '0.85rem'
        }}>
          <span style={{ color: 'var(--text-subtle)' }}>Active Profile:</span>
          <span className="badge badge-purple">{profile?.niches?.join(', ') || 'Fitness'}</span>
          <span className="badge badge-cyan">{profile?.languages?.join(', ') || 'Telugu'}</span>
          <span className="badge badge-amber">{profile?.target_audience || 'Beginners'}</span>
          <span className="badge badge-emerald">{profile?.filming_time || '30 mins'}</span>
          <span className="badge" style={{ background: 'rgba(255, 255, 255, 0.08)', color: 'var(--text-main)' }}>
            {profile?.environment || 'Gym'}
          </span>

          <button
            onClick={onOpenProfile}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--primary-light)',
              textDecoration: 'underline',
              cursor: 'pointer',
              fontWeight: 600,
              marginLeft: '0.5rem',
              fontSize: '0.82rem'
            }}
          >
            Edit Profile
          </button>
        </div>

        {/* Primary CTA and Tweak Controls */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button
            className="btn-primary"
            style={{ padding: '0.85rem 2rem', fontSize: '1.05rem' }}
            onClick={handleGenerateIdeas}
            disabled={loading}
          >
            <Sparkles size={18} className={loading ? 'pulse' : ''} />
            <span>{loading ? 'Generating Ideas...' : 'Generate Ideas'}</span>
          </button>

          <button
            className="btn-secondary"
            onClick={() => setShowFilters(!showFilters)}
            style={{ padding: '0.85rem 1.2rem' }}
          >
            <SlidersHorizontal size={16} />
            <span>{showFilters ? 'Hide Adjustments' : 'Adjust Filming Session'}</span>
          </button>
        </div>
      </div>

      {/* Optional Session Adjustments Drawer */}
      {showFilters && (
        <div className="card" style={{ maxWidth: '780px', margin: '0 auto 2.5rem', background: 'var(--bg-card-elevated)', border: '1px solid var(--border-active)' }}>
          <h3 style={{ fontSize: '1.05rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <SlidersHorizontal size={18} color="var(--primary-light)" />
            Adjust Today's Specific Filming Constraints
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Available Time Today</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. 20 minutes"
                value={overrideTime}
                onChange={e => setOverrideTime(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Location / Environment Today</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Gym corner / Home desk"
                value={overrideEnv}
                onChange={e => setOverrideEnv(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Session Goal</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Grow audience, Educate"
                value={overrideGoal}
                onChange={e => setOverrideGoal(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group" style={{ marginTop: '0.5rem' }}>
            <label className="form-label">Specific Topic or Inspiration Note (Optional)</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. I want to talk about bench press grip or diet protein under ₹50"
              value={additionalNotes}
              onChange={e => setAdditionalNotes(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
            <button className="btn-primary" onClick={handleGenerateIdeas} disabled={loading}>
              <RefreshCw size={15} />
              <span>Generate With These Adjustments</span>
            </button>
          </div>
        </div>
      )}

      {errorMsg && (
        <div style={{ maxWidth: '780px', margin: '0 auto 1.5rem', padding: '0.85rem 1.25rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 'var(--radius-sm)', color: '#fb7185' }}>
          {errorMsg}
        </div>
      )}

      {/* Today's Ideas Section (Exactly 5 personalized cards) */}
      <div style={{ maxWidth: '1020px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div>
            <h2 style={{ fontSize: '1.5rem' }}>Today's Ideas</h2>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              AI-generated content suggestions based on your profile (not verified trend statistics).
            </span>
          </div>

          <span style={{ fontSize: '0.82rem', color: 'var(--text-subtle)' }}>
            Showing {ideas.length} tailored ideas
          </span>
        </div>

        {initialLoading ? (
          <div style={{ textAlign: 'center', padding: '4rem 1rem' }}>
            <Sparkles size={36} color="var(--primary-light)" className="pulse" />
            <p style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>
              Analyzing your creator profile and building tailored content ideas...
            </p>
          </div>
        ) : ideas.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3.5rem 1rem' }}>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>No ideas generated yet.</p>
            <button className="btn-primary" onClick={handleGenerateIdeas} disabled={loading}>
              Generate Ideas Now
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {ideas.map((idea, idx) => (
              <div
                key={idea.id || idx}
                className="card card-interactive"
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '1rem',
                  borderLeft: `4px solid ${idx === 0 ? 'var(--primary)' : 'var(--cyan)'}`
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
                  <div style={{ flex: 1, minWidth: '260px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.45rem' }}>
                      <span className="badge badge-purple">{idea.format || 'Educational Reel'}</span>
                      <span className={`badge ${getDifficultyBadge(idea.difficulty)}`}>
                        {idea.difficulty || 'Easy'}
                      </span>
                      <span className="badge badge-cyan" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                        <Clock size={12} />
                        {idea.estimated_time || '30 mins'}
                      </span>
                    </div>

                    <h3 style={{ fontSize: '1.35rem', lineHeight: 1.3, color: 'var(--text-main)', marginBottom: '0.4rem' }}>
                      {idea.title}
                    </h3>

                    <p style={{ color: 'var(--text-muted)', fontSize: '0.94rem', lineHeight: 1.55 }}>
                      {idea.description}
                    </p>
                  </div>
                </div>

                {/* Why This Fits You Box */}
                <div style={{
                  background: 'rgba(139, 92, 246, 0.08)',
                  border: '1px solid rgba(139, 92, 246, 0.2)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '0.75rem 1rem',
                  fontSize: '0.88rem',
                  color: 'var(--text-main)'
                }}>
                  <strong style={{ color: 'var(--primary-light)', display: 'block', fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.2rem' }}>
                    Why this fits your profile:
                  </strong>
                  {idea.why_it_fits}
                </div>

                {/* Action Toolbar */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <button
                      className="btn-ghost"
                      style={{ fontSize: '0.82rem', padding: '0.4rem 0.65rem' }}
                      title="This idea was useful"
                      onClick={(e) => { e.stopPropagation(); onOpenFeedback(idea.id, null, 'useful'); }}
                    >
                      <ThumbsUp size={14} color="#10b981" />
                      <span>Useful</span>
                    </button>

                    <button
                      className="btn-ghost"
                      style={{ fontSize: '0.82rem', padding: '0.4rem 0.65rem' }}
                      title="This idea wasn't useful"
                      onClick={(e) => { e.stopPropagation(); onOpenFeedback(idea.id, null, 'not_useful'); }}
                    >
                      <ThumbsDown size={14} color="#f43f5e" />
                      <span>Not useful</span>
                    </button>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                    <button
                      className="btn-secondary"
                      style={{ padding: '0.5rem 0.9rem', fontSize: '0.86rem' }}
                      onClick={() => onSelectIdeaForDetail(idea)}
                    >
                      <Eye size={15} />
                      <span>Inspect Idea</span>
                    </button>

                    <button
                      className="btn-primary"
                      style={{ padding: '0.5rem 1.15rem', fontSize: '0.88rem' }}
                      onClick={() => onGenerateBriefForIdea(idea)}
                    >
                      <span>Generate Brief</span>
                      <ArrowRight size={15} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
