import React, { useState } from 'react';
import { X, Lock, Mail, User, PlayCircle, Sparkles } from 'lucide-react';
import { api, setAuthToken } from '../api';

export default function AuthModal({ isOpen, onClose, onAuthSuccess, onDemoLogin }) {
  if (!isOpen) return null;

  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMsg('');

    try {
      let data;
      if (isRegister) {
        data = await api.register({
          email: email.trim(),
          password,
          display_name: displayName.trim()
        });
      } else {
        data = await api.login({
          email: email.trim(),
          password
        });
      }
      setAuthToken(data.access_token);
      onAuthSuccess(data.user);
      onClose();
    } catch (err) {
      setErrorMsg(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '440px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div>
            <span style={{ fontSize: '0.78rem', color: 'var(--primary-light)', fontWeight: 700, textTransform: 'uppercase' }}>
              Influencer Copilot
            </span>
            <h2 style={{ fontSize: '1.45rem', marginTop: '0.2rem' }}>
              {isRegister ? 'Create Creator Account' : 'Creator Sign In'}
            </h2>
          </div>
          <button className="btn-ghost" onClick={onClose} style={{ padding: '0.35rem' }}>
            <X size={18} />
          </button>
        </div>

        {errorMsg && (
          <div style={{ padding: '0.75rem 1rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 'var(--radius-sm)', color: '#fb7185', fontSize: '0.86rem', marginBottom: '1rem' }}>
            {errorMsg}
          </div>
        )}

        {/* 1-Click Demo Callout */}
        <div style={{
          background: 'rgba(245, 158, 11, 0.1)',
          border: '1px solid rgba(245, 158, 11, 0.25)',
          borderRadius: 'var(--radius-md)',
          padding: '0.85rem 1rem',
          marginBottom: '1.25rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '0.75rem'
        }}>
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.88rem', color: '#fbbf24' }}>Testing without signup?</div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Load Rahul's Telugu fitness profile immediately</div>
          </div>
          <button
            type="button"
            className="btn-secondary"
            style={{ padding: '0.45rem 0.75rem', fontSize: '0.8rem', borderColor: 'rgba(245, 158, 11, 0.4)' }}
            onClick={() => {
              onClose();
              onDemoLogin();
            }}
          >
            <PlayCircle size={14} color="#f59e0b" />
            <span>Launch</span>
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {isRegister && (
            <div className="form-group">
              <label className="form-label">Creator Display Name</label>
              <div style={{ position: 'relative' }}>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Rahul Verma"
                  value={displayName}
                  onChange={e => setDisplayName(e.target.value)}
                  required
                />
              </div>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              className="form-input"
              placeholder="creator@example.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="Minimum 6 characters"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            style={{ width: '100%', marginTop: '0.75rem', padding: '0.85rem' }}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Processing...' : (isRegister ? 'Sign Up as Creator' : 'Sign In')}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          {isRegister ? (
            <span>
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => setIsRegister(false)}
                style={{ background: 'transparent', border: 'none', color: 'var(--primary-light)', fontWeight: 700, cursor: 'pointer' }}
              >
                Sign In
              </button>
            </span>
          ) : (
            <span>
              New creator?{' '}
              <button
                type="button"
                onClick={() => setIsRegister(true)}
                style={{ background: 'transparent', border: 'none', color: 'var(--primary-light)', fontWeight: 700, cursor: 'pointer' }}
              >
                Create Account
              </button>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
