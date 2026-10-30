import React, { useEffect, useRef } from 'react';
import { Message } from '../types';
import { MessageItem } from './MessageItem';

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
  onSelectPrompt: (prompt: string, options?: { search_web?: boolean; emotional_mode?: boolean; generate_image?: boolean }) => void;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  isLoading,
  onSelectPrompt,
}) => {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="messages-container" role="log" aria-live="polite">
      {messages.length === 0 ? (
        <div className="welcome-screen">
          <div className="welcome-icon">✨</div>
          <h2 className="welcome-title">How can I assist you today?</h2>
          <p className="welcome-subtitle">
            I am a Multimodal AI Assistant powered by PostgreSQL pgvector RAG, real-time web search, document management, and compassionate emotional support.
          </p>

          <div className="feature-cards">
            <div
              className="feature-card"
              onClick={() => onSelectPrompt('Summarize key points from the uploaded documents and cite the sources.')}
            >
              <div className="feature-card-icon">📄</div>
              <div className="feature-card-title">Document RAG</div>
              <div className="feature-card-desc">Ask questions grounded in user-uploaded knowledge files.</div>
            </div>

            <div
              className="feature-card"
              onClick={() => onSelectPrompt('What are the latest breakthroughs in AI this week?', { search_web: true })}
            >
              <div className="feature-card-icon">🌐</div>
              <div className="feature-card-title">Live Web Search</div>
              <div className="feature-card-desc">Retrieve real-time web information with verified source links.</div>
            </div>

            <div
              className="feature-card"
              onClick={() => onSelectPrompt("I've been feeling overwhelmed and stressed today. Can we talk?", { emotional_mode: true })}
            >
              <div className="feature-card-icon">💖</div>
              <div className="feature-card-title">Emotional Support</div>
              <div className="feature-card-desc">A safe, nonjudgmental space with practical grounding exercises.</div>
            </div>

            <div
              className="feature-card"
              onClick={() => onSelectPrompt('Draw a peaceful Japanese zen garden with neon cherry blossoms', { generate_image: true })}
            >
              <div className="feature-card-icon">🎨</div>
              <div className="feature-card-title">Multimodal Generation</div>
              <div className="feature-card-desc">Generate images, analyze photos, and synthesize audio responses.</div>
            </div>
          </div>
        </div>
      ) : (
        messages.map((msg) => <MessageItem key={msg.id} message={msg} />)
      )}

      {isLoading && (
        <div className="message-row assistant">
          <div className="message-avatar assistant">✨</div>
          <div className="message-content-wrapper">
            <div className="message-bubble assistant" style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
              <div className="spinner" style={{ width: 14, height: 14 }} />
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Processing multimodal context & generating response...
              </span>
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
};
