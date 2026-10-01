import React, { useState, useEffect } from 'react';
import {
  FolderKanban, Lightbulb, Clock, CheckCircle, Send, Archive,
  ArrowRight, Eye, Trash2, AlertCircle, Sparkles, Filter, LayoutGrid, ListFilter, Film
} from 'lucide-react';
import { api } from '../api';

export default function WorkspaceView({ onSelectBrief, onSelectIdeaForDetail }) {
  const [viewMode, setViewMode] = useState('kanban'); // 'kanban' or 'tabs'
  const [activeTab, setActiveTab] = useState('planned'); // 'ideas', 'planned', 'filmed', 'published', 'archived'
  const [summary, setSummary] = useState(null);
  const [ideas, setIdeas] = useState([]);
  const [briefs, setBriefs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  const loadData = async () => {
    try {
      setLoading(true);
      const [sumRes, ideasRes, briefsRes] = await Promise.all([
        api.getWorkspaceSummary(),
        api.listIdeas(),
        api.listBriefs()
      ]);
      setSummary(sumRes);
      setIdeas(ideasRes);
      setBriefs(briefsRes);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to load workspace.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleUpdateBriefStatus = async (briefId, newStatus) => {
    try {
      await api.updateBriefStatus(briefId, newStatus);
      await loadData();
    } catch (err) {
      alert(err.message || 'Error updating status');
    }
  };

  const handleDeleteBrief = async (briefId) => {
    if (!window.confirm('Are you sure you want to delete this brief?')) return;
    try {
      await api.deleteBrief(briefId);
      await loadData();
    } catch (err) {
      alert(err.message || 'Error deleting brief');
    }
  };

  const stages = [
    { id: 'planned', label: 'PLANNED', count: summary?.planned ?? 0, icon: Clock, color: 'var(--primary)', border: 'rgba(139, 92, 246, 0.4)' },
    { id: 'filmed', label: 'FILMED', count: summary?.filmed ?? 0, icon: Film, color: 'var(--cyan)', border: 'rgba(6, 182, 212, 0.4)' },
    { id: 'published', label: 'PUBLISHED', count: summary?.published ?? 0, icon: Send, color: 'var(--emerald)', border: 'rgba(16, 185, 129, 0.4)' },
    { id: 'archived', label: 'ARCHIVED', count: summary?.archived ?? 0, icon: Archive, color: '#94a3b8', border: 'rgba(148, 163, 184, 0.3)' }
  ];

  const filteredBriefs = briefs.filter(b => b.status === activeTab);

  return (
    <div className="container" style={{ paddingTop: '2rem', paddingBottom: '4rem' }}>
      {/* Workspace Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.75rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <FolderKanban size={22} color="var(--primary-light)" />
            <h1 style={{ fontSize: '2.2rem' }}>Creator Production Workspace</h1>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Track content from initial concept to planning, filming, and self-reported publishing.
          </p>
        </div>

        {/* View Mode Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'var(--bg-card)', padding: '0.3rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
          <button
            onClick={() => setViewMode('kanban')}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              padding: '0.4rem 0.85rem',
              borderRadius: '6px',
              border: 'none',
              background: viewMode === 'kanban' ? 'var(--primary)' : 'transparent',
              color: '#fff',
              fontSize: '0.84rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            <LayoutGrid size={15} />
            <span>Kanban Board</span>
          </button>
          <button
            onClick={() => setViewMode('tabs')}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              padding: '0.4rem 0.85rem',
              borderRadius: '6px',
              border: 'none',
              background: viewMode === 'tabs' ? 'var(--primary)' : 'transparent',
              color: '#fff',
              fontSize: '0.84rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            <ListFilter size={15} />
            <span>Stage Tabs</span>
          </button>
        </div>
      </div>

      {/* Published Status Disclaimer Banner (Section 11) */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.65rem',
        padding: '0.75rem 1rem',
        background: 'rgba(6, 182, 212, 0.08)',
        border: '1px solid rgba(6, 182, 212, 0.25)',
        borderRadius: 'var(--radius-sm)',
        fontSize: '0.84rem',
        color: '#38bdf8',
        marginBottom: '1.75rem'
      }}>
        <AlertCircle size={17} style={{ flexShrink: 0 }} />
        <span>
          <strong>Notice:</strong> Publication and filming statuses are self-reported by you for production tracking. No Instagram API publication verification is implied or performed.
        </span>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <Sparkles size={32} className="pulse" color="var(--primary-light)" />
          <p style={{ marginTop: '0.75rem', color: 'var(--text-muted)' }}>Loading workspace items...</p>
        </div>
      ) : viewMode === 'kanban' ? (
        /* ================= 4-COLUMN KANBAN BOARD VIEW (Section 15) ================= */
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1.25rem',
          alignItems: 'start'
        }}>
          {stages.map(stage => {
            const Icon = stage.icon;
            const stageBriefs = briefs.filter(b => b.status === stage.id);
            return (
              <div
                key={stage.id}
                style={{
                  backgroundColor: 'rgba(15, 23, 42, 0.65)',
                  borderRadius: '12px',
                  border: `1px solid ${stage.border}`,
                  padding: '1rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.85rem',
                  minHeight: '400px'
                }}
              >
                {/* Column Header */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '0.65rem', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Icon size={16} color={stage.color} />
                    <span style={{ fontWeight: 800, fontSize: '0.86rem', letterSpacing: '0.05em', color: stage.color }}>
                      {stage.label}
                    </span>
                  </div>
                  <span style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    color: '#fff',
                    borderRadius: '9999px',
                    padding: '2px 8px',
                    fontSize: '0.75rem',
                    fontWeight: 700
                  }}>
                    {stageBriefs.length}
                  </span>
                </div>

                {/* Cards in Column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', flex: 1 }}>
                  {stageBriefs.length === 0 ? (
                    <div style={{
                      textAlign: 'center',
                      padding: '2.5rem 1rem',
                      color: 'var(--text-subtle)',
                      fontSize: '0.82rem',
                      border: '1px dashed rgba(255, 255, 255, 0.08)',
                      borderRadius: '8px'
                    }}>
                      No briefs in {stage.label.toLowerCase()}
                    </div>
                  ) : (
                    stageBriefs.map(b => (
                      <div
                        key={b.id}
                        className="card"
                        style={{
                          padding: '1rem',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '0.65rem',
                          borderLeft: `4px solid ${stage.color}`
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', flexWrap: 'wrap' }}>
                          <span className="badge badge-purple" style={{ fontSize: '0.7rem' }}>v{b.version}</span>
                          <span className="badge badge-amber" style={{ fontSize: '0.7rem' }}>{b.shots?.length || 0} Shots</span>
                        </div>

                        <h4 style={{ fontSize: '1rem', fontWeight: 700, margin: 0, lineHeight: 1.35 }}>
                          {b.title}
                        </h4>

                        {b.caption && (
                          <p style={{ fontSize: '0.78rem', color: 'var(--text-subtle)', lineClamp: 2, margin: 0 }}>
                            {b.caption.slice(0, 80)}...
                          </p>
                        )}

                        {/* Quick Actions */}
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.4rem', marginTop: '0.35rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
                          <button
                            className="btn-ghost"
                            onClick={() => onSelectBrief(b)}
                            style={{ padding: '0.3rem 0.6rem', fontSize: '0.78rem', color: 'var(--primary-light)' }}
                            title="Open in Ready to Shoot Studio"
                          >
                            <Eye size={13} />
                            <span>Studio</span>
                          </button>

                          {/* Quick Stage Mover Buttons */}
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                            {stage.id === 'planned' && (
                              <button
                                className="btn-secondary"
                                onClick={() => handleUpdateBriefStatus(b.id, 'filmed')}
                                style={{ padding: '0.25rem 0.55rem', fontSize: '0.74rem', background: 'rgba(6, 182, 212, 0.15)', borderColor: 'rgba(6, 182, 212, 0.4)', color: '#38bdf8' }}
                                title="Advance to Filmed"
                              >
                                Mark Filmed →
                              </button>
                            )}

                            {stage.id === 'filmed' && (
                              <button
                                className="btn-secondary"
                                onClick={() => handleUpdateBriefStatus(b.id, 'published')}
                                style={{ padding: '0.25rem 0.55rem', fontSize: '0.74rem', background: 'rgba(16, 185, 129, 0.15)', borderColor: 'rgba(16, 185, 129, 0.4)', color: '#34d399' }}
                                title="Advance to Published"
                              >
                                Mark Published →
                              </button>
                            )}

                            {stage.id === 'published' && (
                              <button
                                className="btn-secondary"
                                onClick={() => handleUpdateBriefStatus(b.id, 'archived')}
                                style={{ padding: '0.25rem 0.55rem', fontSize: '0.74rem', color: '#94a3b8' }}
                                title="Move to Archive"
                              >
                                Archive
                              </button>
                            )}

                            <button
                              className="btn-ghost"
                              onClick={() => handleDeleteBrief(b.id)}
                              style={{ padding: '0.3rem', color: '#f43f5e' }}
                              title="Delete Brief"
                            >
                              <Trash2 size={13} />
                            </button>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* ================= STAGE TABS VIEW ================= */
        <>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            overflowX: 'auto',
            paddingBottom: '0.5rem',
            marginBottom: '1.5rem',
            borderBottom: '1px solid var(--border-subtle)'
          }}>
            {[
              { id: 'ideas', label: 'Ideas Bank', count: summary?.ideas ?? ideas.length, icon: Lightbulb },
              { id: 'planned', label: 'Planned Briefs', count: summary?.planned ?? 0, icon: Clock },
              { id: 'filmed', label: 'Filmed', count: summary?.filmed ?? 0, icon: CheckCircle },
              { id: 'published', label: 'Published', count: summary?.published ?? 0, icon: Send },
              { id: 'archived', label: 'Archived', count: summary?.archived ?? 0, icon: Archive }
            ].map(tab => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.65rem 1.15rem',
                    borderRadius: 'var(--radius-sm)',
                    background: isActive ? 'rgba(139, 92, 246, 0.18)' : 'transparent',
                    border: `1px solid ${isActive ? 'var(--primary)' : 'transparent'}`,
                    color: isActive ? '#fff' : 'var(--text-muted)',
                    fontWeight: 600,
                    fontSize: '0.88rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    whiteSpace: 'nowrap'
                  }}
                >
                  <Icon size={16} />
                  <span>{tab.label}</span>
                  <span style={{
                    background: isActive ? 'var(--primary)' : 'rgba(255, 255, 255, 0.08)',
                    color: '#fff',
                    fontSize: '0.72rem',
                    padding: '2px 7px',
                    borderRadius: 'var(--radius-full)',
                    fontWeight: 700
                  }}>
                    {tab.count}
                  </span>
                </button>
              );
            })}
          </div>

          {activeTab === 'ideas' ? (
            /* Ideas Bank Tab */
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {ideas.length === 0 ? (
                <div className="card" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
                  <p style={{ color: 'var(--text-muted)' }}>No saved ideas found in your ideas bank.</p>
                </div>
              ) : (
                ideas.map((idea) => (
                  <div key={idea.id} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.35rem' }}>
                          <span className="badge badge-purple">{idea.format}</span>
                          <span className="badge badge-emerald">{idea.difficulty || 'Easy'}</span>
                          <span className="badge badge-cyan">{idea.estimated_time}</span>
                        </div>
                        <h3 style={{ fontSize: '1.2rem', marginBottom: '0.3rem' }}>{idea.title}</h3>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.5 }}>
                          {idea.description}
                        </p>
                      </div>

                      <button
                        className="btn-secondary"
                        style={{ padding: '0.45rem 0.85rem', fontSize: '0.84rem' }}
                        onClick={() => onSelectIdeaForDetail(idea)}
                      >
                        <Eye size={14} />
                        <span>View Concept</span>
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          ) : (
            /* Briefs Tab (Planned, Filmed, Published, Archived) */
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {filteredBriefs.length === 0 ? (
                <div className="card" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
                  <p style={{ color: 'var(--text-muted)' }}>
                    No briefs in "{activeTab}" stage right now.
                  </p>
                </div>
              ) : (
                filteredBriefs.map((b) => (
                  <div
                    key={b.id}
                    className="card"
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.85rem',
                      borderLeft: `4px solid ${
                        b.status === 'published' ? 'var(--emerald)' :
                        b.status === 'filmed' ? 'var(--cyan)' :
                        b.status === 'planned' ? 'var(--primary)' : 'var(--text-subtle)'
                      }`
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.35rem' }}>
                          <span className="badge badge-purple">Brief v{b.version}</span>
                          <span className="badge badge-amber" style={{ textTransform: 'uppercase' }}>
                            Hook: {b.selected_hook_type}
                          </span>
                          <span className="badge" style={{ background: 'rgba(255, 255, 255, 0.06)', color: 'var(--text-main)' }}>
                            {b.shots?.length || 0} Shots
                          </span>
                        </div>

                        <h3 style={{ fontSize: '1.25rem', marginBottom: '0.35rem' }}>{b.title}</h3>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', lineClamp: 2 }}>
                          {b.caption?.slice(0, 140)}...
                        </p>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                        {/* Status Changer */}
                        <select
                          style={{
                            background: 'var(--bg-surface)',
                            border: '1px solid var(--border-medium)',
                            color: 'var(--text-main)',
                            padding: '0.45rem 0.75rem',
                            borderRadius: 'var(--radius-sm)',
                            fontSize: '0.82rem',
                            fontWeight: 600,
                            cursor: 'pointer'
                          }}
                          value={b.status}
                          onChange={e => handleUpdateBriefStatus(b.id, e.target.value)}
                        >
                          <option value="planned">Stage: Planned</option>
                          <option value="filmed">Stage: Filmed</option>
                          <option value="published">Stage: Published</option>
                          <option value="archived">Stage: Archived</option>
                        </select>

                        <button
                          className="btn-primary"
                          style={{ padding: '0.45rem 0.95rem', fontSize: '0.84rem' }}
                          onClick={() => onSelectBrief(b)}
                        >
                          <Eye size={14} />
                          <span>Open Studio</span>
                        </button>

                        <button
                          className="btn-ghost"
                          style={{ padding: '0.45rem', color: '#f43f5e' }}
                          title="Delete Brief"
                          onClick={() => handleDeleteBrief(b.id)}
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
