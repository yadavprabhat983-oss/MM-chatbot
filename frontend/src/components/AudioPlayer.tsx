import React, { useRef, useState } from 'react';

interface AudioPlayerProps {
  src: string;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({ src }) => {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().then(() => setIsPlaying(true)).catch(() => setIsPlaying(false));
    }
  };

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 10,
        background: 'rgba(255, 255, 255, 0.05)',
        border: '1px solid var(--border-subtle)',
        padding: '6px 14px',
        borderRadius: 'var(--radius-full)',
        margin: '8px 0',
      }}
    >
      <button
        onClick={togglePlay}
        style={{
          background: 'var(--accent-primary)',
          border: 'none',
          color: '#fff',
          width: 28,
          height: 28,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
        }}
        aria-label={isPlaying ? 'Pause audio' : 'Play audio'}
      >
        {isPlaying ? '⏸' : '▶'}
      </button>
      <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
        {isPlaying ? 'Playing Speech Audio...' : 'Listen to Response (TTS)'}
      </span>
      <audio
        ref={audioRef}
        src={src}
        onEnded={() => setIsPlaying(false)}
        onError={() => setIsPlaying(false)}
        preload="auto"
      />
    </div>
  );
};
