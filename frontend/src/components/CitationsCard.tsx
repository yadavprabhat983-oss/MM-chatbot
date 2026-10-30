import React, { useState } from 'react';
import { SourceCitation } from '../types';

interface CitationsCardProps {
  citations: SourceCitation[];
}

export const CitationsCard: React.FC<CitationsCardProps> = ({ citations }) => {
  const [expanded, setExpanded] = useState(false);

  if (!citations || citations.length === 0) return null;

  const docCount = citations.filter((c) => c.source_type === 'document').length;
  const webCount = citations.filter((c) => c.source_type === 'web').length;

  return (
    <div className="citations-wrapper">
      <div
        className="citations-header"
        onClick={() => setExpanded(!expanded)}
        role="button"
        tabIndex={0}
      >
        <span>
          📚 Referenced Sources ({citations.length})
          {docCount > 0 && ` • 📄 ${docCount} Doc${docCount > 1 ? 's' : ''}`}
          {webCount > 0 && ` • 🌐 ${webCount} Web`}
        </span>
        <span>{expanded ? '▲ Hide' : '▼ View Sources'}</span>
      </div>

      {expanded && (
        <div className="citations-list">
          {citations.map((c, i) => (
            <div key={i} className="citation-card">
              <div className="citation-card-header">
                {c.url ? (
                  <a
                    href={c.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="citation-card-title"
                  >
                    {c.title || c.url} ↗
                  </a>
                ) : (
                  <span className="citation-card-title">
                    📄 {c.title} {c.chunk_index !== undefined ? `(Chunk ${c.chunk_index})` : ''}
                  </span>
                )}
                <span className={`citation-card-type ${c.source_type}`}>
                  {c.source_type === 'document' ? 'Document RAG' : 'Live Web'}
                </span>
              </div>
              <p className="citation-card-snippet">{c.snippet}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
