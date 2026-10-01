import React from 'react';
import { Sparkles, ArrowRight, Video, Target, Clock, Smartphone, CheckCircle, ShieldCheck, PlayCircle, Layers } from 'lucide-react';

export default function LandingPage({ onStartCreating, onDemoLogin, onOpenAuth }) {
  return (
    <div className="landing-view">
      {/* Hero Section */}
      <section style={{ textAlign: 'center', padding: '4.5rem 1rem 3rem', maxWidth: '880px', margin: '0 auto' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', padding: '0.35rem 0.9rem', borderRadius: 'var(--radius-full)', background: 'rgba(139, 92, 246, 0.12)', border: '1px solid rgba(139, 92, 246, 0.3)', marginBottom: '1.5rem' }}>
          <Sparkles size={16} color="var(--primary-light)" />
          <span style={{ fontSize: '0.84rem', fontWeight: 600, color: 'var(--primary-light)' }}>
            Creator-First Content Planning System
          </span>
        </div>

        <h1 style={{ fontSize: '3.2rem', lineHeight: 1.15, marginBottom: '1.25rem' }}>
          Turn your niche, audience & gear into <span className="gradient-text">shootable content</span> in minutes.
        </h1>

        <p style={{ fontSize: '1.2rem', color: 'var(--text-muted)', lineHeight: 1.6, maxWidth: '680px', margin: '0 auto 2.5rem' }}>
          Stop staring at a blank screen. Tell us what kind of creator you are, what equipment you have, and how much time you have. We build your complete reel plan.
        </p>

        {/* Primary Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <button className="btn-primary" style={{ padding: '0.9rem 2rem', fontSize: '1.05rem' }} onClick={onStartCreating}>
            <span>Start Creating Now</span>
            <ArrowRight size={18} />
          </button>

          <button className="btn-secondary" style={{ padding: '0.9rem 1.6rem', fontSize: '1.02rem', borderColor: 'rgba(245, 158, 11, 0.4)' }} onClick={onDemoLogin}>
            <PlayCircle size={20} color="#f59e0b" />
            <span>Try as Rahul (Telugu Fitness Demo)</span>
          </button>
        </div>

        {/* Demo Callout */}
        <p style={{ marginTop: '1rem', fontSize: '0.82rem', color: 'var(--text-subtle)' }}>
          ⚡ 1-click test with pre-seeded creator profile: Fitness • Telugu • 30 mins • Smartphone • Gym
        </p>
      </section>

      {/* Complete Creator Journey Pipeline */}
      <section style={{ margin: '2rem auto', maxWidth: '1080px', padding: '0 1rem' }}>
        <div className="card" style={{ background: 'linear-gradient(180deg, rgba(22, 30, 49, 0.8) 0%, rgba(16, 22, 35, 0.95) 100%)' }}>
          <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
            <span style={{ fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--primary-light)', fontWeight: 700 }}>
              The Production Bridge
            </span>
            <h2 style={{ fontSize: '1.75rem', marginTop: '0.35rem' }}>From Blank Slate to Ready-to-Shoot Reel</h2>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
            gap: '0.85rem',
            textAlign: 'center'
          }}>
            {[
              { step: '1', title: 'Creator Need', desc: 'Niche, audience & time limits' },
              { step: '2', title: 'Personalized Ideas', desc: '5 shootable concepts' },
              { step: '3', title: 'Reel Detail', desc: 'Equipment & originality context' },
              { step: '4', title: 'Two Hooks', desc: 'Direct vs Curiosity' },
              { step: '5', title: 'Timed Script', desc: 'Natural speech breakdown' },
              { step: '6', title: 'Shot List', desc: 'Framing & visual actions' },
              { step: '7', title: 'Workspace', desc: 'Planned → Filmed → Published' }
            ].map((s) => (
              <div key={s.step} style={{
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '1rem 0.6rem'
              }}>
                <div style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '50%',
                  background: 'var(--gradient-brand)',
                  color: '#fff',
                  fontWeight: 800,
                  fontSize: '0.85rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 0.6rem'
                }}>
                  {s.step}
                </div>
                <div style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '0.25rem' }}>{s.title}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{s.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Pillar Highlights */}
      <section style={{ maxWidth: '1080px', margin: '3rem auto 4rem', padding: '0 1rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
              <div style={{ padding: '0.6rem', borderRadius: 'var(--radius-sm)', background: 'rgba(139, 92, 246, 0.15)', color: 'var(--primary-light)' }}>
                <Target size={24} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.15rem' }}>Not a Generic Chatbot</h3>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-subtle)' }}>Structured AI Production Engine</span>
              </div>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.6 }}>
              No vague, conversational fluff. You receive structured JSON briefs with timed scripts, shot lists with camera framing, captions, and platform-appropriate CTAs.
            </p>
          </div>

          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
              <div style={{ padding: '0.6rem', borderRadius: 'var(--radius-sm)', background: 'rgba(6, 182, 212, 0.15)', color: '#38bdf8' }}>
                <Smartphone size={24} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.15rem' }}>Grounded in Your Constraints</h3>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-subtle)' }}>Gear, Environment & Minutes</span>
              </div>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.6 }}>
              Only have a smartphone and 20 minutes in the gym or at home? The Copilot creates concepts that fit your exact setup without demanding studio crews or fancy lighting.
            </p>
          </div>

          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
              <div style={{ padding: '0.6rem', borderRadius: 'var(--radius-sm)', background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
                <ShieldCheck size={24} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.15rem' }}>No False Virality Hype</h3>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-subtle)' }}>Honest & Original Content</span>
              </div>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.6 }}>
              We never fabricate trend numbers or promise "guaranteed 100k views". We provide practical originality guidance and audience-first hooks you can be proud to publish.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
