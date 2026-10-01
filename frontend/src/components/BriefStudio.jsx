import React, { useState, useEffect } from 'react';
import {
  Sparkles, ArrowLeft, Save, RefreshCw, Copy, Check, Trash2, Plus,
  Film, AlignLeft, Layers, ShieldAlert, CheckCircle, Smartphone, MapPin,
  Clock, ThumbsUp, ThumbsDown, Share2, Tag, Info, Tv, Music, Video, Scissors
} from 'lucide-react';
import { api } from '../api';
import TeleprompterModal from './TeleprompterModal';

export default function BriefStudio({
  brief,
  onBack,
  onSaveBriefSuccess,
  onRegenerate,
  onOpenFeedback
}) {
  const [editableBrief, setEditableBrief] = useState(brief);
  const [selectedHookType, setSelectedHookType] = useState(brief.selected_hook_type || 'direct');
  const [isSaving, setIsSaving] = useState(false);
  const [isRegeneratingHooks, setIsRegeneratingHooks] = useState(false);
  const [isTeleprompterOpen, setIsTeleprompterOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [saveSuccessNotice, setSaveSuccessNotice] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    setEditableBrief(brief);
    setSelectedHookType(brief.selected_hook_type || 'direct');
  }, [brief]);

  const handleTitleChange = (val) => {
    setEditableBrief(prev => ({ ...prev, title: val }));
  };

  const handleHookChange = (index, val) => {
    const updatedHooks = [...editableBrief.hooks];
    updatedHooks[index].text = val;
    setEditableBrief(prev => ({ ...prev, hooks: updatedHooks }));
  };

  const handleScriptChange = (index, field, val) => {
    const updatedScript = [...editableBrief.script];
    updatedScript[index][field] = val;
    setEditableBrief(prev => ({ ...prev, script: updatedScript }));
  };

  const handleShotChange = (index, field, val) => {
    const updatedShots = [...editableBrief.shots];
    updatedShots[index][field] = val;
    setEditableBrief(prev => ({ ...prev, shots: updatedShots }));
  };

  const handleAddShot = () => {
    const newOrder = (editableBrief.shots || []).length + 1;
    const newShot = {
      order: newOrder,
      timestamp: '0-5s',
      framing: 'Medium Shot',
      action: 'Describe action or movement',
      dialogue: 'Spoken line or voiceover',
      visual_text: 'On-screen text overlay',
      b_roll: 'Secondary footage',
      audio_suggestion: 'Subtle trending background audio',
      transition: 'Smooth cut'
    };
    setEditableBrief(prev => ({
      ...prev,
      shots: [...(prev.shots || []), newShot]
    }));
  };

  const handleDeleteShot = (index) => {
    const filtered = editableBrief.shots.filter((_, i) => i !== index);
    const reordered = filtered.map((s, idx) => ({ ...s, order: idx + 1 }));
    setEditableBrief(prev => ({ ...prev, shots: reordered }));
  };

  const handleStatusChange = async (newStatus) => {
    try {
      const res = await api.updateBriefStatus(editableBrief.id, newStatus);
      setEditableBrief(res);
      setStatusMessage(`Status updated to "${newStatus}". (Self-reported)`);
      setTimeout(() => setStatusMessage(''), 3500);
    } catch (err) {
      setErrorMessage(err.message || 'Failed to update status.');
    }
  };

  const handleRegenerateHooks = async () => {
    setIsRegeneratingHooks(true);
    setErrorMessage('');
    try {
      const updated = await api.regenerateHooks(editableBrief.id);
      setEditableBrief(updated);
      setStatusMessage('Hooks regenerated with fresh perspectives!');
      setTimeout(() => setStatusMessage(''), 3500);
    } catch (err) {
      setErrorMessage(err.message || 'Could not regenerate hooks.');
    } finally {
      setIsRegeneratingHooks(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setErrorMessage('');
    try {
      const payload = {
        title: editableBrief.title,
        content_objective: editableBrief.content_objective,
        selected_hook_type: selectedHookType,
        recommended_hook: editableBrief.recommended_hook,
        hooks: editableBrief.hooks,
        script: editableBrief.script,
        shots: editableBrief.shots,
        caption: editableBrief.caption,
        cta: editableBrief.cta,
        hashtags: editableBrief.hashtags,
        on_screen_text: editableBrief.on_screen_text,
        requirements: editableBrief.requirements,
        editing_notes: editableBrief.editing_notes,
        b_roll_requirements: editableBrief.b_roll_requirements,
        audio_requirements: editableBrief.audio_requirements,
        assumptions: editableBrief.assumptions,
        originality_notes: editableBrief.originality_notes,
        platform_notes: editableBrief.platform_notes,
        version: editableBrief.version
      };

      const saved = await api.updateBrief(editableBrief.id, payload);
      setEditableBrief(saved);
      setSaveSuccessNotice(true);
      setTimeout(() => setSaveSuccessNotice(false), 3500);
      if (onSaveBriefSuccess) {
        onSaveBriefSuccess(saved);
      }
    } catch (err) {
      setErrorMessage(err.message || 'Error saving brief.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCopyToClipboard = () => {
    const chosenHook = editableBrief.hooks?.find(h => h.type === selectedHookType)?.text || editableBrief.hooks?.[0]?.text;
    
    let text = `🎬 REEL BRIEF: ${editableBrief.title}\n`;
    text += `Objective: ${editableBrief.content_objective || 'Audience education'}\n`;
    text += `Status: ${editableBrief.status} | Version: v${editableBrief.version}\n\n`;
    text += `🎯 ACTIVE HOOK (${selectedHookType.toUpperCase()}):\n"${chosenHook}"\n\n`;
    text += `📜 SCRIPT (Timed breakdown):\n`;
    editableBrief.script?.forEach(s => {
      text += `[${s.section} - ${s.title}]: ${s.content}\n`;
    });
    text += `\n🎥 SHOT LIST:\n`;
    editableBrief.shots?.forEach(shot => {
      text += `Shot ${shot.order || ''} [${shot.timestamp || ''}] (${shot.framing || 'Medium'}): ${shot.action || shot.description || ''}\n`;
      if (shot.visual_text) text += `   Overlay: ${shot.visual_text}\n`;
      if (shot.b_roll) text += `   B-Roll: ${shot.b_roll}\n`;
    });
    text += `\n💬 CAPTION:\n${editableBrief.caption}\n\n`;
    text += `📣 CTA: ${editableBrief.cta}\n\n`;
    if (editableBrief.hashtags?.length) text += `#️⃣ HASHTAGS: ${editableBrief.hashtags.join(' ')}\n\n`;
    text += `⚙️ REQUIREMENTS: ${editableBrief.requirements?.join(', ')}\n`;

    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const activeHook = editableBrief.hooks?.find(h => h.type === selectedHookType);

  return (
    <div className="container" style={{ paddingTop: '1.5rem', paddingBottom: '4rem' }}>
      {/* Top Breadcrumb & Controls Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
        <button className="btn-ghost" onClick={onBack} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
          <ArrowLeft size={18} />
          <span>Back to Ideas / Workspace</span>
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexWrap: 'wrap' }}>
          {/* Status Switcher */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'var(--bg-card)', padding: '0.35rem 0.75rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', fontSize: '0.84rem' }}>
            <span style={{ color: 'var(--text-subtle)' }}>Status:</span>
            <select
              style={{ background: 'transparent', border: 'none', color: 'var(--text-main)', fontWeight: 700, outline: 'none', cursor: 'pointer' }}
              value={editableBrief.status}
              onChange={e => handleStatusChange(e.target.value)}
            >
              <option value="planned" style={{ background: 'var(--bg-card)' }}>Planned</option>
              <option value="filmed" style={{ background: 'var(--bg-card)' }}>Filmed (Self-reported)</option>
              <option value="published" style={{ background: 'var(--bg-card)' }}>Published (Self-reported)</option>
              <option value="archived" style={{ background: 'var(--bg-card)' }}>Archived</option>
            </select>
          </div>

          <span className="badge badge-purple" style={{ fontSize: '0.78rem' }}>
            v{editableBrief.version}
          </span>

          <button
            className="btn-secondary"
            onClick={() => setIsTeleprompterOpen(true)}
            style={{
              padding: '0.55rem 0.95rem',
              fontSize: '0.86rem',
              background: 'rgba(236, 72, 153, 0.12)',
              borderColor: 'rgba(236, 72, 153, 0.35)',
              color: '#f472b6',
              fontWeight: 700
            }}
            title="Open Teleprompter Mode for smooth filming"
          >
            <Tv size={16} />
            <span>Teleprompter Mode</span>
          </button>

          <button className="btn-secondary" onClick={handleCopyToClipboard} style={{ padding: '0.55rem 0.95rem', fontSize: '0.86rem' }}>
            {copied ? <Check size={16} color="#10b981" /> : <Copy size={16} />}
            <span>{copied ? 'Copied Brief!' : 'Copy Script'}</span>
          </button>

          <button className="btn-primary" onClick={handleSave} disabled={isSaving} style={{ padding: '0.55rem 1.25rem', fontSize: '0.88rem' }}>
            <Save size={16} />
            <span>{isSaving ? 'Saving...' : 'Save Brief'}</span>
          </button>
        </div>
      </div>

      {statusMessage && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: 'var(--radius-sm)', color: '#34d399', fontSize: '0.88rem', marginBottom: '1.25rem' }}>
          {statusMessage}
        </div>
      )}

      {saveSuccessNotice && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: 'var(--radius-sm)', color: '#34d399', fontSize: '0.88rem', marginBottom: '1.25rem' }}>
          ✓ Brief v{editableBrief.version} saved successfully!
        </div>
      )}

      {errorMessage && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: 'var(--radius-sm)', color: '#fb7185', fontSize: '0.88rem', marginBottom: '1.25rem' }}>
          {errorMessage}
        </div>
      )}

      {/* Main Studio Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 2fr) minmax(320px, 1fr)', gap: '1.5rem', alignItems: 'start' }}>
        
        {/* Left Column: Title, Objective, Hooks, Script, Storyboard */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* 1 & 2. Title and Content Objective */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <label className="form-label" style={{ color: 'var(--primary-light)', margin: 0 }}>
                1. Reel Title & Objective
              </label>
              {editableBrief.recommended_hook && (
                <span className="badge badge-cyan" style={{ fontSize: '0.74rem' }}>
                  AI Suggests: {editableBrief.recommended_hook.toUpperCase()} HOOK
                </span>
              )}
            </div>

            <input
              type="text"
              className="form-input"
              style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.75rem' }}
              value={editableBrief.title}
              onChange={e => handleTitleChange(e.target.value)}
              placeholder="Reel Title"
            />

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontWeight: 600 }}>Objective:</span>
              <input
                type="text"
                className="form-input"
                style={{ fontSize: '0.85rem', padding: '0.3rem 0.6rem', flex: 1 }}
                value={editableBrief.content_objective || ''}
                onChange={e => setEditableBrief(prev => ({ ...prev, content_objective: e.target.value }))}
                placeholder="e.g. Demystify a technical concept in under 45 seconds"
              />
            </div>
          </div>

          {/* 4, 5, 6. Two-Hook Feature */}
          <div className="card" style={{ border: '1px solid rgba(139, 92, 246, 0.3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
              <div>
                <label className="form-label" style={{ color: 'var(--primary-light)', margin: 0 }}>
                  2. Two-Hook Exploration (Choose Your Angle)
                </label>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-subtle)' }}>
                  Hook 1 (Direct) vs Hook 2 (Curiosity). Choose the one you prefer to deliver on camera.
                </span>
              </div>

              <button
                className="btn-ghost"
                style={{ fontSize: '0.8rem', color: 'var(--primary-light)', padding: '0.35rem 0.6rem' }}
                onClick={handleRegenerateHooks}
                disabled={isRegeneratingHooks}
              >
                <RefreshCw size={13} className={isRegeneratingHooks ? 'pulse' : ''} />
                <span>{isRegeneratingHooks ? 'Regenerating...' : 'Regenerate Hooks'}</span>
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.85rem' }}>
              {editableBrief.hooks?.map((h, idx) => {
                const isSelected = selectedHookType === h.type;
                const isDirect = h.type === 'direct';
                return (
                  <div
                    key={h.type || idx}
                    onClick={() => setSelectedHookType(h.type)}
                    style={{
                      background: isSelected ? 'rgba(139, 92, 246, 0.14)' : 'var(--bg-surface)',
                      border: `2px solid ${isSelected ? 'var(--primary)' : 'var(--border-subtle)'}`,
                      borderRadius: 'var(--radius-md)',
                      padding: '1rem',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      position: 'relative'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <span className={`badge ${isDirect ? 'badge-cyan' : 'badge-amber'}`} style={{ textTransform: 'uppercase' }}>
                        {isDirect ? 'Hook 1 — Direct' : 'Hook 2 — Curiosity'}
                      </span>
                      {isSelected && (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.2rem', color: '#fff', fontSize: '0.75rem', fontWeight: 700, background: 'var(--primary)', padding: '2px 8px', borderRadius: 'var(--radius-full)' }}>
                          <Check size={12} /> Active Hook
                        </span>
                      )}
                    </div>

                    <textarea
                      className="form-textarea"
                      style={{ fontSize: '0.92rem', minHeight: '75px', background: isSelected ? 'rgba(0,0,0,0.2)' : 'var(--bg-input)' }}
                      value={h.text}
                      onChange={e => handleHookChange(idx, e.target.value)}
                      onClick={e => e.stopPropagation()}
                    />
                    <span style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-subtle)', marginTop: '0.25rem' }}>
                      {isDirect ? 'Immediate value proposition' : 'Intriguing question/counter-intuitive insight'}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 7. Full Timed Script */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <div>
                <label className="form-label" style={{ color: 'var(--cyan)', margin: 0 }}>
                  3. Full Timed Script (Pacing Breakdown)
                </label>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-subtle)' }}>
                  Designed for conversational delivery. Launch Teleprompter Mode anytime to practice!
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {editableBrief.script?.map((seg, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'var(--bg-surface)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '0.85rem'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.45rem' }}>
                    <span className="badge badge-purple" style={{ fontSize: '0.75rem' }}>
                      {seg.section}
                    </span>
                    <input
                      type="text"
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--text-main)',
                        fontWeight: 700,
                        fontSize: '0.88rem',
                        outline: 'none',
                        flex: 1
                      }}
                      value={seg.title || ''}
                      onChange={e => handleScriptChange(idx, 'title', e.target.value)}
                      placeholder="Section Title"
                    />
                  </div>
                  <textarea
                    className="form-textarea"
                    style={{ fontSize: '0.92rem', minHeight: '60px' }}
                    value={seg.content}
                    onChange={e => handleScriptChange(idx, 'content', e.target.value)}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* 8. Comprehensive Shot List Storyboard */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
              <div>
                <label className="form-label" style={{ color: 'var(--emerald)', margin: 0 }}>
                  4. Production Shot List & Camera Angles
                </label>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-subtle)' }}>
                  Framing, camera action, dialogue cues, overlays, and B-roll for every shot.
                </span>
              </div>

              <button className="btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }} onClick={handleAddShot}>
                <Plus size={14} />
                <span>Add Shot</span>
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {editableBrief.shots?.map((shot, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'var(--bg-surface)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '0.9rem',
                    position: 'relative'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      <span style={{
                        width: '26px',
                        height: '26px',
                        borderRadius: '50%',
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-medium)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '0.78rem',
                        fontWeight: 700
                      }}>
                        {shot.order || idx + 1}
                      </span>

                      <input
                        type="text"
                        className="form-input"
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.82rem', width: '90px' }}
                        value={shot.timestamp || ''}
                        onChange={e => handleShotChange(idx, 'timestamp', e.target.value)}
                        placeholder="0-3 sec"
                      />

                      <input
                        type="text"
                        className="form-input"
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.82rem', width: '160px' }}
                        value={shot.framing || 'Medium Shot'}
                        onChange={e => handleShotChange(idx, 'framing', e.target.value)}
                        placeholder="Framing (e.g. POV)"
                      />

                      <input
                        type="text"
                        className="form-input"
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.82rem', width: '140px' }}
                        value={shot.transition || 'Cut'}
                        onChange={e => handleShotChange(idx, 'transition', e.target.value)}
                        placeholder="Transition (e.g. Cut / Whip pan)"
                      />
                    </div>

                    <button
                      className="btn-ghost"
                      style={{ padding: '0.3rem', color: '#f43f5e' }}
                      title="Delete shot"
                      onClick={() => handleDeleteShot(idx)}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>

                  <div className="form-group" style={{ marginBottom: '0.5rem' }}>
                    <label style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', marginBottom: '2px', display: 'block' }}>Action & Movement</label>
                    <textarea
                      className="form-textarea"
                      style={{ fontSize: '0.88rem', minHeight: '48px' }}
                      value={shot.action || shot.description || ''}
                      onChange={e => {
                        handleShotChange(idx, 'action', e.target.value);
                        handleShotChange(idx, 'description', e.target.value);
                      }}
                      placeholder="What happens on camera in this shot..."
                    />
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.5rem', fontSize: '0.8rem' }}>
                    <div>
                      <span style={{ fontWeight: 600, color: 'var(--primary-light)', display: 'block', fontSize: '0.74rem' }}>Dialogue / Voiceover:</span>
                      <input
                        type="text"
                        className="form-input"
                        style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem' }}
                        value={shot.dialogue || ''}
                        onChange={e => handleShotChange(idx, 'dialogue', e.target.value)}
                        placeholder="Spoken words..."
                      />
                    </div>

                    <div>
                      <span style={{ fontWeight: 600, color: '#38bdf8', display: 'block', fontSize: '0.74rem' }}>Overlay Text:</span>
                      <input
                        type="text"
                        className="form-input"
                        style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem' }}
                        value={shot.visual_text || ''}
                        onChange={e => handleShotChange(idx, 'visual_text', e.target.value)}
                        placeholder="Text on screen..."
                      />
                    </div>

                    <div>
                      <span style={{ fontWeight: 600, color: '#10b981', display: 'block', fontSize: '0.74rem' }}>B-Roll / Cutaway:</span>
                      <input
                        type="text"
                        className="form-input"
                        style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem' }}
                        value={shot.b_roll || ''}
                        onChange={e => handleShotChange(idx, 'b_roll', e.target.value)}
                        placeholder="Screen recording / close-up..."
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Caption, CTA, Hashtags, Production Notes, Requirements, Assumptions */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* 10, 11, 12. Caption, CTA & Hashtags */}
          <div className="card">
            <label className="form-label" style={{ color: 'var(--amber)', marginBottom: '0.35rem' }}>
              5. Platform Caption
            </label>
            <textarea
              className="form-textarea"
              style={{ minHeight: '120px', fontSize: '0.88rem', marginBottom: '0.85rem' }}
              value={editableBrief.caption}
              onChange={e => setEditableBrief(prev => ({ ...prev, caption: e.target.value }))}
              placeholder="Caption for Instagram, Shorts, TikTok..."
            />

            <label className="form-label" style={{ color: '#fb7185', marginBottom: '0.35rem' }}>
              6. Call-to-Action (CTA)
            </label>
            <input
              type="text"
              className="form-input"
              style={{ marginBottom: '0.85rem' }}
              value={editableBrief.cta}
              onChange={e => setEditableBrief(prev => ({ ...prev, cta: e.target.value }))}
              placeholder="e.g. Save this reel & comment CODE for the template"
            />

            <label className="form-label" style={{ color: 'var(--cyan)', marginBottom: '0.35rem' }}>
              7. Hashtag Suggestions
            </label>
            <input
              type="text"
              className="form-input"
              value={(editableBrief.hashtags || []).join(' ')}
              onChange={e => setEditableBrief(prev => ({ ...prev, hashtags: e.target.value.split(' ').filter(Boolean) }))}
              placeholder="#techtips #productivity #codingtips"
            />
          </div>

          {/* 9. On-Screen Text Overlays */}
          {editableBrief.on_screen_text?.length > 0 && (
            <div className="card">
              <label className="form-label" style={{ color: '#38bdf8', marginBottom: '0.5rem' }}>
                8. Master On-Screen Text Overlays
              </label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                {editableBrief.on_screen_text.map((txt, i) => (
                  <div key={i} style={{ padding: '0.45rem 0.75rem', background: 'var(--bg-surface)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', fontSize: '0.84rem' }}>
                    📌 {txt}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 13 & 14. Requirements & Estimated Filming Time */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <label className="form-label" style={{ color: 'var(--emerald)', margin: 0 }}>
                9. Filming Requirements
              </label>
              <span className="badge badge-gray" style={{ fontSize: '0.72rem' }}>
                <Clock size={12} style={{ marginRight: '3px' }} />
                ~30 min shoot
              </span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {editableBrief.requirements?.map((req, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.4rem', fontSize: '0.84rem', color: 'var(--text-main)' }}>
                  <CheckCircle size={15} color="#10b981" style={{ marginTop: '2px', flexShrink: 0 }} />
                  <span>{req}</span>
                </div>
              ))}
            </div>
          </div>

          {/* 15, 16, 17. Editing, B-roll & Audio Notes */}
          <div className="card" style={{ border: '1px solid rgba(59, 130, 246, 0.25)' }}>
            <label className="form-label" style={{ color: '#60a5fa', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <Scissors size={15} /> 10. Post-Production & Audio Guidance
            </label>
            
            {editableBrief.editing_notes?.length > 0 && (
              <div style={{ marginBottom: '0.65rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-subtle)', display: 'block', marginBottom: '2px' }}>Editing:</span>
                {editableBrief.editing_notes.map((note, idx) => (
                  <div key={idx} style={{ fontSize: '0.82rem', color: 'var(--text-main)', marginBottom: '2px' }}>• {note}</div>
                ))}
              </div>
            )}

            {editableBrief.b_roll_requirements?.length > 0 && (
              <div style={{ marginBottom: '0.65rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-subtle)', display: 'block', marginBottom: '2px' }}>B-Roll Captures:</span>
                {editableBrief.b_roll_requirements.map((br, idx) => (
                  <div key={idx} style={{ fontSize: '0.82rem', color: 'var(--text-main)', marginBottom: '2px' }}>• {br}</div>
                ))}
              </div>
            )}

            {editableBrief.audio_requirements?.length > 0 && (
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-subtle)', display: 'block', marginBottom: '2px' }}>Audio/Voiceover:</span>
                {editableBrief.audio_requirements.map((aud, idx) => (
                  <div key={idx} style={{ fontSize: '0.82rem', color: 'var(--text-main)', marginBottom: '2px' }}>• {aud}</div>
                ))}
              </div>
            )}
          </div>

          {/* 18. Explicit AI Assumptions */}
          <div className="card">
            <label className="form-label" style={{ color: 'var(--text-subtle)', marginBottom: '0.5rem' }}>
              11. Transparent Assumptions
            </label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {editableBrief.assumptions?.map((ass, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.4rem', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  <Info size={14} color="var(--primary-light)" style={{ marginTop: '2px', flexShrink: 0 }} />
                  <span>{ass}</span>
                </div>
              ))}
            </div>
          </div>

          {/* 19 & 20. Originality & Platform Adaptation */}
          <div className="card" style={{ background: 'rgba(245, 158, 11, 0.06)', border: '1px solid rgba(245, 158, 11, 0.25)' }}>
            <label className="form-label" style={{ color: '#fbbf24', marginBottom: '0.5rem' }}>
              12. Originality & Platform Optimization
            </label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {editableBrief.originality_notes?.map((note, i) => (
                <div key={i} style={{ fontSize: '0.82rem', color: 'var(--text-main)', lineHeight: 1.45 }}>
                  • {note}
                </div>
              ))}
              {editableBrief.platform_notes?.map((pnote, i) => (
                <div key={`p-${i}`} style={{ fontSize: '0.82rem', color: 'var(--text-subtle)', lineHeight: 1.45, fontStyle: 'italic' }}>
                  📱 {pnote}
                </div>
              ))}
            </div>
          </div>

          {/* Feedback & Actions Box */}
          <div className="card" style={{ textAlign: 'center', padding: '1.25rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, display: 'block', marginBottom: '0.65rem' }}>
              Was this reel brief useful?
            </span>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}>
              <button
                className="btn-secondary"
                style={{ fontSize: '0.84rem', padding: '0.45rem 0.85rem' }}
                onClick={() => onOpenFeedback(editableBrief.idea_id, editableBrief.id, 'useful')}
              >
                <ThumbsUp size={15} color="#10b981" />
                <span>Useful 👍</span>
              </button>
              <button
                className="btn-secondary"
                style={{ fontSize: '0.84rem', padding: '0.45rem 0.85rem' }}
                onClick={() => onOpenFeedback(editableBrief.idea_id, editableBrief.id, 'not_useful')}
              >
                <ThumbsDown size={15} color="#f43f5e" />
                <span>Not useful 👎</span>
              </button>
            </div>
          </div>

        </div>
      </div>

      {/* Teleprompter Mode Modal */}
      <TeleprompterModal
        isOpen={isTeleprompterOpen}
        onClose={() => setIsTeleprompterOpen(false)}
        script={editableBrief.script}
        title={editableBrief.title}
        selectedHook={activeHook?.text}
      />
    </div>
  );
}
