import React, { useState, useEffect } from 'react';
import { DocumentDetail, DocumentAIEditResponse } from '../types';
import { api } from '../services/api';

interface DocumentEditorProps {
  documentId: number;
  onBack: () => void;
  onDocumentDeleted: (id: number) => void;
  onDocumentUpdated: () => void;
}

export const DocumentEditor: React.FC<DocumentEditorProps> = ({
  documentId,
  onBack,
  onDocumentDeleted,
  onDocumentUpdated,
}) => {
  const [doc, setDoc] = useState<DocumentDetail | null>(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [selectedVersionId, setSelectedVersionId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [customPrompt, setCustomPrompt] = useState('');
  const [proposedDiff, setProposedDiff] = useState<DocumentAIEditResponse | null>(null);
  const [statusMsg, setStatusMsg] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const loadDocument = async () => {
    setIsLoading(true);
    try {
      const data = await api.getDocument(documentId);
      setDoc(data);
      setTitle(data.title);
      setContent(data.content_text);
      if (data.versions.length > 0) {
        setSelectedVersionId(data.versions[0].id);
      }
    } catch (err: any) {
      setStatusMsg({ text: `Failed to load document: ${err.message}`, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDocument();
  }, [documentId]);

  const handleVersionChange = (versionId: number) => {
    if (!doc) return;
    setSelectedVersionId(versionId);
    const ver = doc.versions.find((v) => v.id === versionId);
    if (ver) {
      setContent(ver.content_text);
    }
  };

  const handleSave = async () => {
    if (!doc) return;
    setIsSaving(true);
    setStatusMsg(null);
    try {
      const updated = await api.updateDocument(doc.id, content, title, 'Manual editor update');
      setDoc(updated);
      onDocumentUpdated();
      setStatusMsg({ text: 'Saved successfully and re-indexed for RAG!', type: 'success' });
    } catch (err: any) {
      setStatusMsg({ text: `Save failed: ${err.message}`, type: 'error' });
    } finally {
      setIsSaving(false);
    }
  };

  const handleAiEdit = async (action: string, customInstruction?: string) => {
    if (!doc) return;
    setIsAiLoading(true);
    setProposedDiff(null);
    setStatusMsg(null);
    try {
      const instruction = customInstruction || `Please ${action} this text to improve clarity.`;
      const diff = await api.aiEditDocument(doc.id, action, instruction);
      setProposedDiff(diff);
    } catch (err: any) {
      setStatusMsg({ text: `AI Edit failed: ${err.message}`, type: 'error' });
    } finally {
      setIsAiLoading(false);
    }
  };

  const handleAcceptDiff = () => {
    if (!proposedDiff) return;
    setContent(proposedDiff.proposed_text);
    setProposedDiff(null);
    setStatusMsg({ text: 'AI proposed changes applied to editor. Click "Save & Re-index" to commit.', type: 'success' });
  };

  const handleReindex = async () => {
    if (!doc) return;
    setIsSaving(true);
    try {
      const res = await api.reindexDocument(doc.id);
      setStatusMsg({ text: `Re-indexed into ${res.chunk_count} vector chunks.`, type: 'success' });
      loadDocument();
    } catch (err: any) {
      setStatusMsg({ text: `Re-indexing failed: ${err.message}`, type: 'error' });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!doc) return;
    if (!window.confirm(`Are you sure you want to delete "${doc.title}"? This cannot be undone.`)) return;

    try {
      await api.deleteDocument(doc.id);
      onDocumentDeleted(doc.id);
    } catch (err: any) {
      setStatusMsg({ text: `Delete failed: ${err.message}`, type: 'error' });
    }
  };

  if (isLoading) {
    return (
      <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
        <div className="spinner" style={{ marginBottom: 12 }} />
        <p>Loading document details...</p>
      </div>
    );
  }

  if (!doc) {
    return (
      <div style={{ padding: 40, textAlign: 'center' }}>
        <p>Document not found.</p>
        <button className="editor-btn" onClick={onBack} style={{ marginTop: 12 }}>
          Back to List
        </button>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Top action header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <button className="editor-btn" onClick={onBack}>
          ← Back to Documents
        </button>
        <div style={{ display: 'flex', gap: 8 }}>
          <a
            href={api.getDownloadUrl(doc.id, 'md')}
            download
            className="editor-btn"
            style={{ textDecoration: 'none' }}
          >
            ⬇ .md
          </a>
          <a
            href={api.getDownloadUrl(doc.id, 'txt')}
            download
            className="editor-btn"
            style={{ textDecoration: 'none' }}
          >
            ⬇ .txt
          </a>
          <button className="editor-btn" onClick={handleReindex} disabled={isSaving} title="Rebuild RAG Index">
            🔄 Re-index
          </button>
          <button
            className="editor-btn"
            onClick={handleDelete}
            style={{ color: 'var(--danger)', borderColor: 'rgba(239, 68, 68, 0.4)' }}
          >
            🗑 Delete
          </button>
        </div>
      </div>

      {statusMsg && (
        <div
          style={{
            padding: '10px 14px',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.85rem',
            background: statusMsg.type === 'success' ? 'var(--success-bg)' : 'var(--danger-bg)',
            color: statusMsg.type === 'success' ? 'var(--success)' : 'var(--danger)',
            border: `1px solid ${statusMsg.type === 'success' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
          }}
        >
          {statusMsg.text}
        </div>
      )}

      {/* Title & Metadata */}
      <div>
        <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
          Document Title
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          style={{
            width: '100%',
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '8px 12px',
            color: 'var(--text-primary)',
            fontSize: '0.95rem',
            fontWeight: 600,
          }}
        />
      </div>

      {/* Version Selector */}
      {doc.versions.length > 1 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Version History:</span>
          <select
            value={selectedVersionId || ''}
            onChange={(e) => handleVersionChange(Number(e.target.value))}
            style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-primary)',
              borderRadius: 'var(--radius-sm)',
              padding: '4px 8px',
              fontSize: '0.8rem',
            }}
          >
            {doc.versions.map((v) => (
              <option key={v.id} value={v.id}>
                v{v.version_number} — {v.change_summary || 'Update'} ({new Date(v.created_at).toLocaleTimeString()})
              </option>
            ))}
          </select>
        </div>
      )}

      {/* AI Assistance Toolbar */}
      <div className="editor-toolbar">
        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', alignSelf: 'center' }}>
          AI Assist:
        </span>
        <button
          className="editor-btn"
          onClick={() => handleAiEdit('summarize')}
          disabled={isAiLoading}
          id="btn-ai-summarize"
        >
          📝 Summarize
        </button>
        <button
          className="editor-btn"
          onClick={() => handleAiEdit('expand')}
          disabled={isAiLoading}
          id="btn-ai-expand"
        >
          📈 Expand
        </button>
        <button
          className="editor-btn"
          onClick={() => handleAiEdit('rewrite')}
          disabled={isAiLoading}
          id="btn-ai-rewrite"
        >
          ✨ Rewrite
        </button>
        <button
          className="editor-btn"
          onClick={() => handleAiEdit('grammar')}
          disabled={isAiLoading}
          id="btn-ai-grammar"
        >
          🔍 Fix Grammar
        </button>
      </div>

      {/* Custom AI instruction input */}
      <div style={{ display: 'flex', gap: 8 }}>
        <input
          type="text"
          placeholder="Custom AI edit instruction (e.g., 'Turn into FAQ format')..."
          value={customPrompt}
          onChange={(e) => setCustomPrompt(e.target.value)}
          style={{
            flex: 1,
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '6px 10px',
            fontSize: '0.82rem',
            color: 'var(--text-primary)',
          }}
        />
        <button
          className="editor-btn"
          onClick={() => handleAiEdit('custom', customPrompt)}
          disabled={!customPrompt.trim() || isAiLoading}
        >
          Apply Custom Prompt
        </button>
      </div>

      {isAiLoading && (
        <div style={{ textAlign: 'center', padding: 12, color: 'var(--text-accent)' }}>
          <div className="spinner" style={{ marginRight: 8 }} /> AI is generating proposed changes...
        </div>
      )}

      {/* AI Proposed Changes Review Diff */}
      {proposedDiff && (
        <div className="diff-box">
          <div className="diff-header">
            <span>✨ AI Proposed Revision ({proposedDiff.diff_summary})</span>
            <div style={{ display: 'flex', gap: 8 }}>
              <button
                className="editor-btn primary"
                onClick={handleAcceptDiff}
                style={{ fontSize: '0.78rem', padding: '4px 10px' }}
                id="btn-accept-diff"
              >
                ✓ Accept Changes
              </button>
              <button
                className="editor-btn"
                onClick={() => setProposedDiff(null)}
                style={{ fontSize: '0.78rem', padding: '4px 10px' }}
                id="btn-discard-diff"
              >
                ✕ Discard
              </button>
            </div>
          </div>
          <div
            style={{
              maxHeight: 180,
              overflowY: 'auto',
              fontSize: '0.82rem',
              color: 'var(--text-primary)',
              whiteSpace: 'pre-wrap',
              background: 'rgba(0, 0, 0, 0.2)',
              padding: 10,
              borderRadius: 6,
            }}
          >
            {proposedDiff.proposed_text}
          </div>
        </div>
      )}

      {/* Text Editor */}
      <div>
        <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
          Content (Markdown / Plain Text)
        </label>
        <textarea
          className="editor-textarea"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Document text goes here..."
          id="document-content-editor"
        />
      </div>

      {/* Save Button */}
      <button
        className="editor-btn primary"
        onClick={handleSave}
        disabled={isSaving}
        style={{ padding: '10px 20px', fontSize: '0.9rem', width: '100%' }}
        id="btn-save-document"
      >
        {isSaving ? 'Saving & Re-indexing...' : '💾 Save & Re-index RAG'}
      </button>
    </div>
  );
};
