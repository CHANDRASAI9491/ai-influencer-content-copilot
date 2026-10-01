import React, { useState } from 'react';
import { X, Check, Sparkles, Smartphone, Clock, MapPin, Target, Film, Layers, Award, Radio, Shield, Palette } from 'lucide-react';
import { api } from '../api';

const CREATOR_TYPES = [
  'Aspiring Influencer',
  'Established Creator',
  'Individual Content Creator'
];

const NICHES_LIST = [
  'Fitness', 'Technology', 'Education', 'Finance', 'Fashion',
  'Beauty', 'Food', 'Travel', 'Gaming', 'Comedy',
  'Lifestyle', 'Business', 'Motivation', 'Custom...'
];

const LANGUAGES_LIST = [
  'English', 'Telugu', 'Hindi', 'Tamil', 'Kannada', 'Malayalam', 'Spanish', 'French'
];

const GOALS_LIST = [
  'Grow audience', 'Increase engagement', 'Build personal brand',
  'Educate', 'Entertain', 'Promote products', 'Generate leads'
];

const FORMATS_LIST = [
  'Talking head', 'Tutorial', 'Storytelling', 'Educational',
  'Comedy', 'Listicle', 'Challenge', 'Before/after', 'Review', 'POV'
];

const EQUIPMENT_LIST = [
  'Smartphone', 'Tripod', 'Microphone', 'Camera', 'Lighting',
  'Laptop', 'Editing software', 'No special equipment'
];

const ENVIRONMENTS_LIST = [
  'Bedroom / Desk setup', 'Gym', 'Outdoor', 'Home', 'Office', 'Studio', 'College campus'
];

const TIME_OPTIONS = [
  '15 minutes', '30 minutes', '45 minutes', '1 hour', '2+ hours'
];

const EXPERIENCE_LEVELS = ['Beginner', 'Intermediate', 'Advanced'];
const DURATION_OPTIONS = ['15-30 seconds', '30-60 seconds', '60-90 seconds'];
const TONE_OPTIONS = [
  'Simple, practical, energetic',
  'Educational & Authoritative',
  'Casual & Conversational',
  'Humorous & Entertaining',
  'Inspirational & Motivating'
];
const PLATFORMS_LIST = ['Instagram Reels', 'YouTube Shorts', 'TikTok'];
const FREQUENCY_OPTIONS = ['Daily', '3-4 times a week', '1-2 times a week', 'Weekly'];

export default function OnboardingModal({ isOpen, onClose, currentProfile, onProfileSaved }) {
  if (!isOpen) return null;

  const initialNiche = currentProfile?.niches?.[0] || 'Technology';
  const isCustomInitial = !NICHES_LIST.filter(n => n !== 'Custom...').includes(initialNiche);

  const [creatorType, setCreatorType] = useState(currentProfile?.creator_type || 'Aspiring Influencer');
  const [nicheSelection, setNicheSelection] = useState(isCustomInitial ? 'Custom...' : initialNiche);
  const [customNiche, setCustomNiche] = useState(isCustomInitial ? initialNiche : '');
  const [languages, setLanguages] = useState(currentProfile?.languages || ['English']);
  const [targetAudience, setTargetAudience] = useState(currentProfile?.target_audience || 'College students and beginners');
  const [broadLocation, setBroadLocation] = useState(currentProfile?.broad_location || 'Global');
  const [goals, setGoals] = useState(currentProfile?.goals || ['Grow audience', 'Educate']);
  const [formats, setFormats] = useState(currentProfile?.formats || ['Educational', 'Tutorial', 'POV']);
  const [equipment, setEquipment] = useState(currentProfile?.equipment || ['Smartphone']);
  const [filmingTime, setFilmingTime] = useState(currentProfile?.filming_time || '1 hour');
  const [environment, setEnvironment] = useState(currentProfile?.environment || 'Bedroom / Desk setup');
  
  // Section 5 newly supported fields
  const [experienceLevel, setExperienceLevel] = useState(currentProfile?.experience_level || 'Beginner');
  const [preferredDuration, setPreferredDuration] = useState(currentProfile?.preferred_duration || '30-60 seconds');
  const [tone, setTone] = useState(currentProfile?.tone || 'Simple, practical, energetic');
  const [platforms, setPlatforms] = useState(currentProfile?.platforms || ['Instagram Reels']);
  const [postingFrequency, setPostingFrequency] = useState(currentProfile?.posting_frequency || '3-4 times a week');
  const [topicsLiked, setTopicsLiked] = useState((currentProfile?.topics_liked || ['Productivity', 'Tech shortcuts', 'AI tools']).join(', '));
  const [topicsAvoided, setTopicsAvoided] = useState((currentProfile?.topics_avoided || ['Get-rich-quick', 'Controversy']).join(', '));

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const toggleItem = (list, setList, item) => {
    if (list.includes(item)) {
      setList(list.filter(x => x !== item));
    } else {
      setList([...list, item]);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMsg('');

    const finalNiche = nicheSelection === 'Custom...' ? (customNiche.trim() || 'General') : nicheSelection;

    try {
      const payload = {
        creator_type: creatorType,
        niches: [finalNiche],
        secondary_niches: [],
        languages: languages.length ? languages : ['English'],
        target_audience: targetAudience.trim() || 'General audience',
        broad_location: broadLocation.trim() || 'Global',
        goals: goals.length ? goals : ['Grow audience'],
        formats: formats.length ? formats : ['Educational'],
        equipment: equipment.length ? equipment : ['Smartphone'],
        filming_time: filmingTime,
        environment: environment,
        experience_level: experienceLevel,
        preferred_duration: preferredDuration,
        tone: tone,
        platforms: platforms.length ? platforms : ['Instagram Reels'],
        posting_frequency: postingFrequency,
        topics_liked: topicsLiked.split(',').map(s => s.trim()).filter(Boolean),
        topics_avoided: topicsAvoided.split(',').map(s => s.trim()).filter(Boolean)
      };

      const updated = await api.updateProfile(payload);
      onProfileSaved(updated);
      onClose();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to save creator profile.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content modal-large" style={{ maxHeight: '90vh', overflowY: 'auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div>
            <span style={{ fontSize: '0.78rem', color: 'var(--primary-light)', fontWeight: 700, textTransform: 'uppercase' }}>
              Creator Profile & Personalization Hub
            </span>
            <h2 style={{ fontSize: '1.6rem', marginTop: '0.2rem' }}>Configure Your Creator DNA</h2>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-subtle)', margin: 0 }}>
              Tailor every content idea and reel brief precisely to your niche, audience, and filming realities.
            </p>
          </div>
          <button className="btn-ghost" onClick={onClose} style={{ padding: '0.4rem' }}>
            <X size={20} />
          </button>
        </div>

        {errorMsg && (
          <div style={{ padding: '0.75rem 1rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 'var(--radius-sm)', color: '#fb7185', fontSize: '0.88rem', marginBottom: '1rem' }}>
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSave}>
          {/* Section 1: Basic Identity & Niche */}
          <div style={{ marginBottom: '1.5rem', paddingBottom: '1.25rem', borderBottom: '1px solid var(--border-subtle)' }}>
            <h3 style={{ fontSize: '1.05rem', marginBottom: '0.75rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <Layers size={18} color="var(--primary-light)" />
              1. Creator Identity & Niche
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Creator Stage</label>
                <select className="form-select" value={creatorType} onChange={e => setCreatorType(e.target.value)}>
                  {CREATOR_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Primary Niche</label>
                <select className="form-select" value={nicheSelection} onChange={e => setNicheSelection(e.target.value)}>
                  {NICHES_LIST.map(n => <option key={n} value={n}>{n}</option>)}
                </select>
              </div>

              {nicheSelection === 'Custom...' && (
                <div className="form-group">
                  <label className="form-label">Custom Niche Name</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Sustainable Woodworking, Indie Game Dev"
                    value={customNiche}
                    onChange={e => setCustomNiche(e.target.value)}
                    required
                  />
                </div>
              )}

              <div className="form-group">
                <label className="form-label">Experience Level</label>
                <select className="form-select" value={experienceLevel} onChange={e => setExperienceLevel(e.target.value)}>
                  {EXPERIENCE_LEVELS.map(lvl => <option key={lvl} value={lvl}>{lvl}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Target Audience</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. College students, beginner techies"
                  value={targetAudience}
                  onChange={e => setTargetAudience(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Location / Target Market</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. India, United States, Global"
                  value={broadLocation}
                  onChange={e => setBroadLocation(e.target.value)}
                />
              </div>
            </div>

            {/* Languages */}
            <div className="form-group" style={{ marginTop: '0.85rem' }}>
              <label className="form-label">Languages (Primary & Secondary)</label>
              <div className="pill-grid">
                {LANGUAGES_LIST.map(lang => (
                  <div
                    key={lang}
                    className={`pill-option ${languages.includes(lang) ? 'active' : ''}`}
                    onClick={() => toggleItem(languages, setLanguages, lang)}
                  >
                    {languages.includes(lang) && <Check size={14} />}
                    {lang}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Section 2: Style, Formats & Goals */}
          <div style={{ marginBottom: '1.5rem', paddingBottom: '1.25rem', borderBottom: '1px solid var(--border-subtle)' }}>
            <h3 style={{ fontSize: '1.05rem', marginBottom: '0.75rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <Palette size={18} color="#06b6d4" />
              2. Content Style, Formats & Goals
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '0.85rem' }}>
              <div className="form-group">
                <label className="form-label">Tone & Style</label>
                <select className="form-select" value={tone} onChange={e => setTone(e.target.value)}>
                  {TONE_OPTIONS.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Preferred Reel Duration</label>
                <select className="form-select" value={preferredDuration} onChange={e => setPreferredDuration(e.target.value)}>
                  {DURATION_OPTIONS.map(d => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Posting Frequency</label>
                <select className="form-select" value={postingFrequency} onChange={e => setPostingFrequency(e.target.value)}>
                  {FREQUENCY_OPTIONS.map(f => <option key={f} value={f}>{f}</option>)}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Active Platforms</label>
              <div className="pill-grid">
                {PLATFORMS_LIST.map(p => (
                  <div
                    key={p}
                    className={`pill-option ${platforms.includes(p) ? 'active' : ''}`}
                    onClick={() => toggleItem(platforms, setPlatforms, p)}
                  >
                    {platforms.includes(p) && <Check size={14} />}
                    {p}
                  </div>
                ))}
              </div>
            </div>

            <div className="form-group" style={{ marginTop: '0.75rem' }}>
              <label className="form-label">Content Goals</label>
              <div className="pill-grid">
                {GOALS_LIST.map(g => (
                  <div
                    key={g}
                    className={`pill-option ${goals.includes(g) ? 'active' : ''}`}
                    onClick={() => toggleItem(goals, setGoals, g)}
                  >
                    {goals.includes(g) && <Check size={14} />}
                    {g}
                  </div>
                ))}
              </div>
            </div>

            <div className="form-group" style={{ marginTop: '0.75rem' }}>
              <label className="form-label">Preferred Formats</label>
              <div className="pill-grid">
                {FORMATS_LIST.map(f => (
                  <div
                    key={f}
                    className={`pill-option ${formats.includes(f) ? 'active' : ''}`}
                    onClick={() => toggleItem(formats, setFormats, f)}
                  >
                    {formats.includes(f) && <Check size={14} />}
                    {f}
                  </div>
                ))}
              </div>
            </div>

            {/* Topics Liked and Avoided */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginTop: '0.85rem' }}>
              <div className="form-group">
                <label className="form-label">Topics You Like (Comma-separated)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. AI tools, productivity tips, desk gear"
                  value={topicsLiked}
                  onChange={e => setTopicsLiked(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Topics to Avoid (Comma-separated)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Crypto hype, politics, drama"
                  value={topicsAvoided}
                  onChange={e => setTopicsAvoided(e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Section 3: Equipment & Filming Realities */}
          <div style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.05rem', marginBottom: '0.75rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <Smartphone size={18} color="#10b981" />
              3. Available Equipment & Filming Constraints
            </h3>

            <div className="form-group">
              <label className="form-label">Available Equipment</label>
              <div className="pill-grid">
                {EQUIPMENT_LIST.map(eq => (
                  <div
                    key={eq}
                    className={`pill-option ${equipment.includes(eq) ? 'active' : ''}`}
                    onClick={() => toggleItem(equipment, setEquipment, eq)}
                  >
                    {equipment.includes(eq) && <Check size={14} />}
                    {eq}
                  </div>
                ))}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginTop: '0.75rem' }}>
              <div className="form-group">
                <label className="form-label">Available Filming Time</label>
                <select className="form-select" value={filmingTime} onChange={e => setFilmingTime(e.target.value)}>
                  {TIME_OPTIONS.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Filming Environment</label>
                <select className="form-select" value={environment} onChange={e => setEnvironment(e.target.value)}>
                  {ENVIRONMENTS_LIST.map(env => <option key={env} value={env}>{env}</option>)}
                </select>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : 'Save Profile & Update Copilot'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
