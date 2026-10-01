import React, { useState } from 'react';
import { X, ThumbsUp, ThumbsDown, CheckCircle, MessageSquare } from 'lucide-react';
import { api } from '../api';

const NOT_USEFUL_REASONS = [
  'Too generic',
  'Not relevant to my niche',
  'Too difficult to create',
  'Requires equipment I don\'t have',
  'Doesn\'t fit my audience',
  'Language/style problem',
  'Other'
];

export default function FeedbackModal({
  isOpen,
  onClose,
  ideaId,
  briefId,
  initialRating = 'useful'
}) {
  if (!isOpen) return null;

  const [rating, setRating] = useState(initialRating);
  const [selectedReason, setSelectedReason] = useState('Too generic');
  const [details, setDetails] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMsg('');

    try {
      await api.submitFeedback({
        idea_id: ideaId || undefined,
        brief_id: briefId || undefined,
        rating: rating,
        reason: rating === 'not_useful' ? selectedReason : undefined,
        details: details.trim() || undefined
      });
      setSubmitted(true);
      setTimeout(() => {
        setSubmitted(false);
        onClose();
      }, 1500);
    } catch (err) {
      setErrorMsg(err.message || 'Error submitting feedback.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '500px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
            <MessageSquare size={18} color="var(--primary-light)" />
            Was this content useful?
          </h3>
          <button className="btn-ghost" onClick={onClose} style={{ padding: '0.35rem' }}>
            <X size={18} />
          </button>
        </div>

        {submitted ? (
          <div style={{ textAlign: 'center', padding: '2rem 1rem' }}>
            <CheckCircle size={36} color="#10b981" style={{ margin: '0 auto 0.75rem' }} />
            <h4 style={{ fontSize: '1.15rem', color: 'var(--text-main)' }}>Thank you for your feedback!</h4>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.25rem' }}>
              Your response will help tune future content generations to your preferences.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            {errorMsg && (
              <div style={{ padding: '0.65rem 0.9rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 'var(--radius-sm)', color: '#fb7185', fontSize: '0.85rem', marginBottom: '1rem' }}>
                {errorMsg}
              </div>
            )}

            {/* Rating Buttons */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.25rem' }}>
              <button
                type="button"
                className={`btn-secondary ${rating === 'useful' ? 'active' : ''}`}
                style={{
                  padding: '0.75rem',
                  borderColor: rating === 'useful' ? '#10b981' : 'var(--border-medium)',
                  background: rating === 'useful' ? 'rgba(16, 185, 129, 0.15)' : 'var(--bg-card)'
                }}
                onClick={() => setRating('useful')}
              >
                <ThumbsUp size={18} color="#10b981" />
                <span style={{ fontWeight: 700 }}>👍 Useful</span>
              </button>

              <button
                type="button"
                className={`btn-secondary ${rating === 'not_useful' ? 'active' : ''}`}
                style={{
                  padding: '0.75rem',
                  borderColor: rating === 'not_useful' ? '#f43f5e' : 'var(--border-medium)',
                  background: rating === 'not_useful' ? 'rgba(244, 63, 94, 0.15)' : 'var(--bg-card)'
                }}
                onClick={() => setRating('not_useful')}
              >
                <ThumbsDown size={18} color="#f43f5e" />
                <span style={{ fontWeight: 700 }}>👎 Not useful</span>
              </button>
            </div>

            {/* Why not useful question */}
            {rating === 'not_useful' && (
              <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                <label className="form-label">Why wasn't this useful?</label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
                  {NOT_USEFUL_REASONS.map(reason => (
                    <label
                      key={reason}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.5rem 0.75rem',
                        background: 'var(--bg-card)',
                        border: `1px solid ${selectedReason === reason ? 'var(--primary)' : 'var(--border-subtle)'}`,
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.88rem',
                        cursor: 'pointer'
                      }}
                    >
                      <input
                        type="radio"
                        name="feedback_reason"
                        checked={selectedReason === reason}
                        onChange={() => setSelectedReason(reason)}
                      />
                      <span>{reason}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Optional Comments / Suggestions</label>
              <textarea
                className="form-textarea"
                placeholder="What could be improved for your workflow?"
                style={{ minHeight: '70px', fontSize: '0.88rem' }}
                value={details}
                onChange={e => setDetails(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.65rem', marginTop: '1rem' }}>
              <button type="button" className="btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="btn-primary" disabled={isSubmitting}>
                {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
