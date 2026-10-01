import React from 'react';
import { X, Sparkles, Clock, Target, Smartphone, MapPin, Lightbulb, ArrowRight, ShieldCheck } from 'lucide-react';

export default function IdeaDetailModal({ isOpen, onClose, idea, onCreateMyReel }) {
  if (!isOpen || !idea) return null;

  const equipmentList = idea.meta_info?.required_equipment || ['Smartphone'];
  const env = idea.meta_info?.shooting_environment || 'Gym';
  const originality = idea.meta_info?.originality_considerations || 'Share your own relatable mistakes from your first month to connect authentically.';

  return (
    <div className="modal-overlay">
      <div className="modal-content modal-large">
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
              <span className="badge badge-purple">{idea.format}</span>
              <span className="badge badge-emerald">{idea.difficulty || 'Easy'}</span>
              <span className="badge badge-cyan">{idea.estimated_time}</span>
            </div>
            <h2 style={{ fontSize: '1.75rem', lineHeight: 1.25, color: 'var(--text-main)' }}>
              {idea.title}
            </h2>
          </div>
          <button className="btn-ghost" onClick={onClose} style={{ padding: '0.4rem' }}>
            <X size={20} />
          </button>
        </div>

        {/* Concept description */}
        <div style={{ marginBottom: '1.5rem', padding: '1rem', background: 'var(--bg-card)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
          <h4 style={{ fontSize: '0.84rem', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.4rem' }}>
            Reel Concept & Hook Premise
          </h4>
          <p style={{ fontSize: '1.02rem', lineHeight: 1.6, color: 'var(--text-main)' }}>
            {idea.description}
          </p>
        </div>

        {/* Specifications Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
          {/* Why fits */}
          <div style={{ padding: '0.9rem', background: 'rgba(139, 92, 246, 0.08)', border: '1px solid rgba(139, 92, 246, 0.25)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--primary-light)', fontWeight: 700, fontSize: '0.82rem', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
              <Sparkles size={14} />
              Why this fits you
            </div>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
              {idea.why_it_fits}
            </p>
          </div>

          {/* Target Audience & Format */}
          <div style={{ padding: '0.9rem', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#06b6d4', fontWeight: 700, fontSize: '0.82rem', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
              <Target size={14} />
              Target Audience
            </div>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-main)' }}>
              College students & beginners looking for accessible advice without intimidation.
            </p>
          </div>

          {/* Required Gear */}
          <div style={{ padding: '0.9rem', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#10b981', fontWeight: 700, fontSize: '0.82rem', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
              <Smartphone size={14} />
              Required Equipment
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '0.25rem' }}>
              {equipmentList.map(eq => (
                <span key={eq} className="badge" style={{ background: 'rgba(255, 255, 255, 0.05)', color: 'var(--text-main)' }}>
                  {eq}
                </span>
              ))}
            </div>
          </div>

          {/* Shooting Environment */}
          <div style={{ padding: '0.9rem', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#f59e0b', fontWeight: 700, fontSize: '0.82rem', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
              <MapPin size={14} />
              Shooting Environment
            </div>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-main)', marginTop: '0.25rem' }}>
              {env} (quiet corner / simple prop)
            </p>
          </div>
        </div>

        {/* Originality Considerations */}
        <div style={{ padding: '1rem', background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.25)', borderRadius: 'var(--radius-md)', marginBottom: '1.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', color: '#fbbf24', fontWeight: 700, fontSize: '0.85rem', marginBottom: '0.4rem' }}>
            <Lightbulb size={16} />
            Originality Considerations
          </div>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', lineHeight: 1.55 }}>
            {originality}
          </p>
          <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-subtle)', marginTop: '0.4rem' }}>
            💡 Tip: Do not copy another creator's exact wording. Transform the core lesson through your own authentic point of view.
          </span>
        </div>

        {/* Footer Actions */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.75rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
          <button className="btn-secondary" onClick={onClose}>
            Back to Ideas
          </button>
          <button
            className="btn-primary"
            style={{ padding: '0.8rem 1.6rem', fontSize: '1rem' }}
            onClick={() => {
              onClose();
              onCreateMyReel(idea);
            }}
          >
            <span>Create My Reel</span>
            <ArrowRight size={17} />
          </button>
        </div>
      </div>
    </div>
  );
}
