import React, { useState, useEffect, useRef } from 'react';
import { DocumentItem } from '../types';
import { api } from '../services/api';
import { DocumentEditor } from './DocumentEditor';
import { Modal } from './Modal';

interface DocumentWorkspaceProps {
  isOpen: boolean;
  onClose: () => void;
  onDocumentsChanged: () => void;
}

export const DocumentWorkspace: React.FC<DocumentWorkspaceProps> = ({
  isOpen,
  onClose,
  onDocumentsChanged,
}) => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // New doc form
  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');

  const uploadInputRef = useRef<HTMLInputElement | null>(null);

  const fetchDocs = async () => {
    setIsLoading(true);
    try {
      const data = await api.listDocuments();
      setDocuments(data);
    } catch (err) {
      console.error('Failed to load documents:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchDocs();
    }
  }, [isOpen]);

  const handleUploadFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      await api.uploadDocument(file);
      await fetchDocs();
      onDocumentsChanged();
    } catch (err: any) {
      alert(`Upload failed: ${err.message}`);
    } finally {
      setIsUploading(false);
      if (uploadInputRef.current) uploadInputRef.current.value = '';
    }
  };

  const handleCreateDocument = async () => {
    if (!newTitle.trim() || !newContent.trim()) return;

    try {
      await api.createDocument(newTitle.trim(), newContent.trim());
      setNewTitle('');
      setNewContent('');
      setIsCreateModalOpen(false);
      await fetchDocs();
      onDocumentsChanged();
    } catch (err: any) {
      alert(`Creation failed: ${err.message}`);
    }
  };

  if (!isOpen) return null;

  return (
    <aside className="doc-workspace-drawer" role="complementary" aria-label="Document Workspace">
      <div className="workspace-header">
        <h2>📚 Document Workspace & RAG</h2>
        <button className="btn-icon-composer" onClick={onClose} aria-label="Close workspace">
          ✕
        </button>
      </div>

      <div className="workspace-content">
        {selectedDocId ? (
          <DocumentEditor
            documentId={selectedDocId}
            onBack={() => setSelectedDocId(null)}
            onDocumentDeleted={() => {
              setSelectedDocId(null);
              fetchDocs();
              onDocumentsChanged();
            }}
            onDocumentUpdated={() => {
              fetchDocs();
              onDocumentsChanged();
            }}
          />
        ) : (
          <>
            {/* Action buttons */}
            <div style={{ display: 'flex', gap: 10 }}>
              <input
                type="file"
                ref={uploadInputRef}
                onChange={handleUploadFile}
                accept=".pdf,.txt,.md,.docx"
                style={{ display: 'none' }}
                id="doc-upload-input"
              />
              <button
                className="editor-btn primary"
                style={{ flex: 1, padding: '10px 14px' }}
                onClick={() => uploadInputRef.current?.click()}
                disabled={isUploading}
                id="btn-upload-document"
              >
                {isUploading ? 'Uploading & Indexing...' : '⬆ Upload Document'}
              </button>
              <button
                className="editor-btn"
                style={{ flex: 1, padding: '10px 14px' }}
                onClick={() => setIsCreateModalOpen(true)}
                id="btn-create-document"
              >
                + New Document
              </button>
            </div>

            {/* Document list info */}
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Uploaded documents are automatically chunked, embedded, and indexed with pgvector for RAG question answering.
            </div>

            {/* Documents List */}
            {isLoading ? (
              <div style={{ textAlign: 'center', padding: 30, color: 'var(--text-muted)' }}>
                <div className="spinner" style={{ marginBottom: 10 }} />
                <p>Loading indexed documents...</p>
              </div>
            ) : documents.length === 0 ? (
              <div
                style={{
                  textAlign: 'center',
                  padding: 40,
                  border: '1px dashed var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--text-muted)',
                }}
              >
                <div style={{ fontSize: '2rem', marginBottom: 10 }}>📄</div>
                <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>
                  No documents in knowledge base
                </p>
                <p style={{ fontSize: '0.8rem' }}>
                  Upload a PDF, TXT, Markdown, or Word DOCX file to enable semantic vector retrieval.
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="doc-item-card"
                    onClick={() => setSelectedDocId(doc.id)}
                  >
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: 4 }}>
                        {doc.title}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', gap: 8 }}>
                        <span>.{doc.file_type}</span>
                        <span>•</span>
                        <span>{Math.round(doc.file_size / 1024)} KB</span>
                        <span>•</span>
                        <span>{doc.chunk_count} vector chunks</span>
                      </div>
                    </div>

                    <span className={`doc-status-badge ${doc.status}`}>
                      {doc.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* Create Document Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Knowledge Document"
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>
              Document Title
            </label>
            <input
              type="text"
              placeholder="e.g., Team Guidelines or Product FAQ"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              style={{
                width: '100%',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '8px 12px',
                color: 'var(--text-primary)',
              }}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: 4 }}>
              Initial Content (Markdown)
            </label>
            <textarea
              placeholder="Write or paste document contents here..."
              rows={8}
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              style={{
                width: '100%',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '10px',
                color: 'var(--text-primary)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.85rem',
              }}
            />
          </div>

          <div className="modal-footer">
            <button className="editor-btn" onClick={() => setIsCreateModalOpen(false)}>
              Cancel
            </button>
            <button
              className="editor-btn primary"
              onClick={handleCreateDocument}
              disabled={!newTitle.trim() || !newContent.trim()}
            >
              Create & Index
            </button>
          </div>
        </div>
      </Modal>
    </aside>
  );
};
