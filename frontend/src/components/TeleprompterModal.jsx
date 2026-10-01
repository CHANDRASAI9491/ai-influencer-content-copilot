import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, X, RotateCcw, Type, ChevronUp, ChevronDown, Clock } from 'lucide-react';

export default function TeleprompterModal({ isOpen, onClose, script, title, selectedHook }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [fontSize, setFontSize] = useState(36); // in px
  const [scrollSpeed, setScrollSpeed] = useState(2); // pixels per tick
  const scrollContainerRef = useRef(null);

  // Reset scroll when opened
  useEffect(() => {
    if (isOpen) {
      setIsPlaying(false);
      if (scrollContainerRef.current) {
        scrollContainerRef.current.scrollTop = 0;
      }
    }
  }, [isOpen]);

  // Handle auto-scroll loop
  useEffect(() => {
    let animId;
    if (isPlaying) {
      const scrollLoop = () => {
        if (scrollContainerRef.current) {
          scrollContainerRef.current.scrollTop += scrollSpeed * 0.5;
        }
        animId = requestAnimationFrame(scrollLoop);
      };
      animId = requestAnimationFrame(scrollLoop);
    }
    return () => cancelAnimationFrame(animId);
  }, [isPlaying, scrollSpeed]);

  // Keyboard shortcut listener (Space to play/pause, Esc to close, Arrow keys for speed)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return;
      if (e.code === 'Space') {
        e.preventDefault();
        setIsPlaying(prev => !prev);
      } else if (e.code === 'Escape') {
        onClose();
      } else if (e.code === 'ArrowUp') {
        e.preventDefault();
        setScrollSpeed(prev => Math.min(prev + 1, 8));
      } else if (e.code === 'ArrowDown') {
        e.preventDefault();
        setScrollSpeed(prev => Math.max(prev - 1, 1));
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 1000,
      backgroundColor: '#05070f',
      color: '#f8fafc',
      display: 'flex',
      flexDirection: 'column',
      fontFamily: 'Inter, system-ui, sans-serif',
      userSelect: 'none'
    }}>
      {/* Top Floating Teleprompter HUD Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0.9rem 1.5rem',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        backgroundColor: 'rgba(10, 15, 30, 0.95)',
        backdropFilter: 'blur(8px)',
        flexWrap: 'wrap',
        gap: '1rem',
        zIndex: 10
      }}>
        {/* Title & Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{
            background: 'linear-gradient(135deg, #ec4899, #8b5cf6)',
            padding: '3px 9px',
            borderRadius: '4px',
            fontSize: '0.75rem',
            fontWeight: 800,
            letterSpacing: '0.05em'
          }}>
            PROMPTER
          </span>
          <h2 style={{ fontSize: '1.05rem', fontWeight: 700, margin: 0, maxWidth: '350px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {title}
          </h2>
        </div>

        {/* Controls: Play/Pause, Speed, Font Size */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          {/* Play / Pause */}
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 1.25rem',
              backgroundColor: isPlaying ? '#f43f5e' : '#10b981',
              color: '#ffffff',
              border: 'none',
              borderRadius: '9999px',
              fontWeight: 700,
              fontSize: '0.9rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            {isPlaying ? <Pause size={17} /> : <Play size={17} />}
            <span>{isPlaying ? 'Pause' : 'Start Scroll'}</span>
          </button>

          {/* Reset button */}
          <button
            onClick={() => {
              setIsPlaying(false);
              if (scrollContainerRef.current) scrollContainerRef.current.scrollTop = 0;
            }}
            title="Reset to Top"
            style={{
              padding: '0.5rem 0.75rem',
              backgroundColor: 'rgba(255, 255, 255, 0.08)',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              borderRadius: '6px',
              color: '#cbd5e1',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              fontSize: '0.84rem'
            }}
          >
            <RotateCcw size={15} />
            <span>Top</span>
          </button>

          {/* Speed Adjust */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', background: 'rgba(255, 255, 255, 0.06)', padding: '0.25rem 0.6rem', borderRadius: '6px' }}>
            <span style={{ fontSize: '0.78rem', color: '#94a3b8', marginRight: '0.2rem' }}>Speed:</span>
            <button
              onClick={() => setScrollSpeed(s => Math.max(s - 1, 1))}
              disabled={scrollSpeed <= 1}
              style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer', padding: '2px 4px' }}
            >
              <ChevronDown size={16} />
            </button>
            <span style={{ fontWeight: 800, fontSize: '0.88rem', minWidth: '20px', textAlign: 'center' }}>{scrollSpeed}x</span>
            <button
              onClick={() => setScrollSpeed(s => Math.min(s + 1, 8))}
              disabled={scrollSpeed >= 8}
              style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer', padding: '2px 4px' }}
            >
              <ChevronUp size={16} />
            </button>
          </div>

          {/* Font Size Adjust */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', background: 'rgba(255, 255, 255, 0.06)', padding: '0.25rem 0.6rem', borderRadius: '6px' }}>
            <Type size={14} color="#94a3b8" />
            <button
              onClick={() => setFontSize(f => Math.max(f - 4, 22))}
              style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer', fontWeight: 800, fontSize: '0.85rem' }}
              title="Decrease Font Size"
            >
              A-
            </button>
            <span style={{ fontSize: '0.78rem', color: '#cbd5e1', margin: '0 2px' }}>{fontSize}px</span>
            <button
              onClick={() => setFontSize(f => Math.min(f + 6, 64))}
              style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer', fontWeight: 800, fontSize: '1rem' }}
              title="Increase Font Size"
            >
              A+
            </button>
          </div>

          {/* Exit Prompter Button */}
          <button
            onClick={onClose}
            style={{
              padding: '0.5rem',
              backgroundColor: 'rgba(255, 255, 255, 0.08)',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              borderRadius: '9999px',
              color: '#fff',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            title="Exit Teleprompter (Esc)"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Prompter Scrolling Canvas */}
      <div
        ref={scrollContainerRef}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '4rem 15% 20rem 15%',
          scrollBehavior: isPlaying ? 'auto' : 'smooth'
        }}
      >
        {/* Selected Hook Hero */}
        {selectedHook && (
          <div style={{
            marginBottom: '3rem',
            padding: '1.5rem',
            borderRadius: '12px',
            backgroundColor: 'rgba(139, 92, 246, 0.12)',
            borderLeft: '5px solid #8b5cf6'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#a78bfa', fontSize: '0.85rem', fontWeight: 700, marginBottom: '0.5rem' }}>
              <Clock size={16} />
              <span>ACTIVE OPENING HOOK</span>
            </div>
            <div style={{ fontSize: `${Math.round(fontSize * 1.15)}px`, fontWeight: 800, lineHeight: 1.35, color: '#ffffff' }}>
              "{selectedHook}"
            </div>
          </div>
        )}

        {/* Timed Script Segments */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '3.5rem' }}>
          {script?.map((sec, idx) => (
            <div key={idx} style={{ position: 'relative' }}>
              {/* Section Header */}
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                padding: '4px 12px',
                borderRadius: '6px',
                fontSize: '0.85rem',
                fontWeight: 700,
                color: '#38bdf8',
                marginBottom: '1rem',
                letterSpacing: '0.03em'
              }}>
                <span>{sec.section}</span>
                <span>•</span>
                <span>{sec.title}</span>
              </div>

              {/* Spoken Dialogue Text */}
              <div style={{
                fontSize: `${fontSize}px`,
                fontWeight: 600,
                lineHeight: 1.5,
                color: '#f8fafc',
                letterSpacing: '-0.01em',
                textShadow: '0 2px 10px rgba(0,0,0,0.5)'
              }}>
                {sec.content}
              </div>
            </div>
          ))}
        </div>

        {/* Prompter End Marker */}
        <div style={{
          marginTop: '6rem',
          textAlign: 'center',
          color: '#64748b',
          fontSize: '1.1rem',
          fontWeight: 700,
          borderTop: '1px dashed rgba(255, 255, 255, 0.15)',
          paddingTop: '2rem'
        }}>
          🎬 END OF REEL SCRIPT • GOOD TAKE!
        </div>
      </div>

      {/* Bottom Minimal Hint */}
      <div style={{
        padding: '0.5rem 1.5rem',
        textAlign: 'center',
        fontSize: '0.75rem',
        color: '#64748b',
        borderTop: '1px solid rgba(255, 255, 255, 0.05)',
        backgroundColor: '#05070f'
      }}>
        Press <strong>Space</strong> to Play/Pause • <strong>↑/↓</strong> for Speed • <strong>Esc</strong> to Exit Prompter
      </div>
    </div>
  );
}
