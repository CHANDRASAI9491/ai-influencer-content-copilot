import React, { useState } from 'react';
import { X, User, RotateCcw, Check, Sparkles } from 'lucide-react';
import { api } from '../api';

export default function ProfileModal({ isOpen, onClose, profile, onProfileUpdated }) {
  if (!isOpen) return null;

  const [creatorType, setCreatorType] = useState(profile?.creator_type || 'Aspiring Influencer');
  const [niches, setNiches] = useState(profile?.niches?.join(', ') || 'Fitness');
  const [languages, setLanguages] = useState(profile?.languages?.join(', ') || 'Telugu, English');
  const [targetAudience, setTargetAudience] = useState(profile?.target_audience || 'College students and beginners');
  const [filmingTime, setFilmingTime] = useState(profile?.filming_time || '30 minutes');
  const [equipment, setEquipment] = useState(profile?.equipment?.join(', ') || 'Smartphone');
  const [environment, setEnvironment] = useState(profile?.environment || 'Gym');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');

  const handleSave = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setStatusMsg('');
    try {
      const payload = {
        creator_type: creatorType,
        niches: niches.split(',').map(s => s.trim()).filter(Boolean),
        languages: languages.split(',').map(s => s.trim()).filter(Boolean),
        target_audience: targetAudience.trim(),
        filming_time: filmingTime.trim(),
        equipment: equipment.split(',').map(s => s.trim()).filter(Boolean),
        environment: environment.trim()
      };
      const updated = await api.updateProfile(payload);
      onProfileUpdated(updated);
      setStatusMsg('Profile preferences updated successfully!');
      setTimeout(() => {
        setStatusMsg('');
        onClose();
      }, 1200);
    } catch (err) {
      alert(err.message || 'Error updating profile');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResetToDemo = async () => {
    if (!window.confirm('Reset this profile to Rahul\'s demo profile (Telugu Fitness Creator)?')) return;
    setIsSubmitting(true);
    try {
      const demoProfile = await api.resetDemoProfile();
      onProfileUpdated(demoProfile);
      setCreatorType(demoProfile.creator_type);
      setNiches(demoProfile.niches.join(', '));
      setLanguages(demoProfile.languages.join(', '));
      setTargetAudience(demoProfile.target_audience);
      setFilmingTime(demoProfile.filming_time);
      setEquipment(demoProfile.equipment.join(', '));
      setEnvironment(demoProfile.environment);
      setStatusMsg('Reset to Rahul (Demo Creator) successfully!');
      setTimeout(() => setStatusMsg(''), 2500);
    } catch (err) {
      alert(err.message || 'Error resetting profile');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '580px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div>
            <span style={{ fontSize: '0.78rem', color: 'var(--primary-light)', fontWeight: 700, textTransform: 'uppercase' }}>
              Creator Preferences
            </span>
            <h2 style={{ fontSize: '1.5rem', marginTop: '0.2rem' }}>Edit Creator Context</h2>
          </div>
          <button className="btn-ghost" onClick={onClose} style={{ padding: '0.35rem' }}>
            <X size={18} />
          </button>
        </div>

        {statusMsg && (
          <div style={{ padding: '0.75rem 1rem', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: 'var(--radius-sm)', color: '#34d399', fontSize: '0.86rem', marginBottom: '1.25rem' }}>
            {statusMsg}
          </div>
        )}

        <form onSubmit={handleSave}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Creator Stage</label>
              <input
                type="text"
                className="form-input"
                value={creatorType}
                onChange={e => setCreatorType(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Niche(s) (comma separated)</label>
              <input
                type="text"
                className="form-input"
                value={niches}
                onChange={e => setNiches(e.target.value)}
                placeholder="Fitness, Nutrition"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Language(s)</label>
              <input
                type="text"
                className="form-input"
                value={languages}
                onChange={e => setLanguages(e.target.value)}
                placeholder="Telugu, English"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Target Audience</label>
              <input
                type="text"
                className="form-input"
                value={targetAudience}
                onChange={e => setTargetAudience(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Available Filming Time</label>
              <input
                type="text"
                className="form-input"
                value={filmingTime}
                onChange={e => setFilmingTime(e.target.value)}
                placeholder="30 minutes"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Shooting Environment</label>
              <input
                type="text"
                className="form-input"
                value={environment}
                onChange={e => setEnvironment(e.target.value)}
                placeholder="Gym / Home"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Equipment (comma separated)</label>
            <input
              type="text"
              className="form-input"
              value={equipment}
              onChange={e => setEquipment(e.target.value)}
              placeholder="Smartphone, Tripod"
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)', flexWrap: 'wrap', gap: '0.75rem' }}>
            <button
              type="button"
              className="btn-secondary"
              style={{ fontSize: '0.84rem', borderColor: 'rgba(245, 158, 11, 0.4)' }}
              onClick={handleResetToDemo}
              disabled={isSubmitting}
            >
              <RotateCcw size={14} color="#f59e0b" />
              <span>Reset to Rahul Demo</span>
            </button>

            <div style={{ display: 'flex', gap: '0.65rem' }}>
              <button type="button" className="btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="btn-primary" disabled={isSubmitting}>
                {isSubmitting ? 'Saving...' : 'Save Preferences'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
