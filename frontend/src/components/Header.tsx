import React from 'react';

interface HeaderProps {
  title: string;
  isEmotionalMode: boolean;
  isWebSearch: boolean;
  documentCount: number;
  onOpenWorkspace: () => void;
  onToggleSidebarMobile: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  isEmotionalMode,
  isWebSearch,
  documentCount,
  onOpenWorkspace,
  onToggleSidebarMobile,
}) => {
  return (
    <header className="chat-header">
      <div className="chat-header-title">
        <button
          className="btn-icon-composer"
          onClick={onToggleSidebarMobile}
          aria-label="Toggle navigation menu"
          style={{ marginRight: 4 }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>
        <h1>{title || 'Multimodal AI Assistant'}</h1>

        {isEmotionalMode && (
          <span className="mode-badge emotional" title="Empathetic listening and supportive care">
            💖 Emotional Support
          </span>
        )}
        {isWebSearch && (
          <span className="mode-badge web-search" title="Live web search enabled">
            🌐 Web Search
          </span>
        )}
      </div>

      <div className="header-actions">
        <button
          className="btn-header-action"
          onClick={onOpenWorkspace}
          id="btn-open-workspace"
          title="Open Document & RAG Knowledge Workspace"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10 9 9 9 8 9" />
          </svg>
          Documents ({documentCount})
        </button>
      </div>
    </header>
  );
};
