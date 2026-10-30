import React, { useState, useRef, ChangeEvent, KeyboardEvent } from 'react';
import { AttachmentItem } from '../types';
import { api } from '../services/api';

interface ComposerProps {
  onSendMessage: (params: {
    message: string;
    search_web: boolean;
    emotional_mode: boolean;
    generate_tts: boolean;
    generate_image: boolean;
    attachments: AttachmentItem[];
  }) => void;
  isLoading: boolean;
  defaultEmotionalMode?: boolean;
}

export const Composer: React.FC<ComposerProps> = ({
  onSendMessage,
  isLoading,
  defaultEmotionalMode = false,
}) => {
  const [text, setText] = useState('');
  const [searchWeb, setSearchWeb] = useState(false);
  const [emotionalMode, setEmotionalMode] = useState(defaultEmotionalMode);
  const [generateTTS, setGenerateTTS] = useState(false);
  const [generateImage, setGenerateImage] = useState(false);
  const [attachments, setAttachments] = useState<AttachmentItem[]>([]);
  const [isTranscribing, setIsTranscribing] = useState(false);

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const audioInputRef = useRef<HTMLInputElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  const handleTextChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    // Auto resize
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if ((!text.trim() && attachments.length === 0) || isLoading) return;

    onSendMessage({
      message: text.trim() || '(Attached file inquiry)',
      search_web: searchWeb,
      emotional_mode: emotionalMode,
      generate_tts: generateTTS,
      generate_image: generateImage,
      attachments,
    });

    setText('');
    setAttachments([]);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleFileSelect = async (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const reader = new FileReader();

      reader.onload = () => {
        const result = reader.result as string;
        const b64 = result.split(',')[1];
        let type: 'image' | 'audio' | 'document' = 'document';

        if (file.type.startsWith('image/')) type = 'image';
        else if (file.type.startsWith('audio/')) type = 'audio';

        setAttachments((prev) => [
          ...prev,
          {
            type,
            filename: file.name,
            content_base64: b64,
            mime_type: file.type,
          },
        ]);
      };
      reader.readAsDataURL(file);
    }

    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleAudioTranscribe = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsTranscribing(true);
    try {
      const res = await api.transcribeAudio(file);
      setText((prev) => (prev ? `${prev} ${res.transcription}` : res.transcription));
    } catch (err: any) {
      alert(`Transcription failed: ${err.message}`);
    } finally {
      setIsTranscribing(false);
      if (audioInputRef.current) audioInputRef.current.value = '';
    }
  };

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="composer-container">
      <div className="composer-box">
        {/* Attachments preview */}
        {attachments.length > 0 && (
          <div className="attachments-preview-row">
            {attachments.map((att, i) => (
              <div key={i} className="attachment-chip">
                <span>
                  {att.type === 'image' ? '🖼️' : att.type === 'audio' ? '🎵' : '📄'} {att.filename}
                </span>
                <button
                  type="button"
                  className="attachment-chip-remove"
                  onClick={() => removeAttachment(i)}
                  title="Remove attachment"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Input textarea */}
        <div className="composer-input-row">
          <textarea
            ref={textareaRef}
            className="composer-textarea"
            placeholder={
              emotionalMode
                ? "Share what's on your mind... I'm here to listen."
                : 'Ask a question, analyze documents, search the web, or attach media...'
            }
            rows={1}
            value={text}
            onChange={handleTextChange}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            id="composer-input"
          />

          <button
            type="button"
            className="btn-send"
            onClick={handleSubmit}
            disabled={(!text.trim() && attachments.length === 0) || isLoading}
            id="btn-send-message"
            aria-label="Send message"
          >
            {isLoading ? (
              <div className="spinner" />
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            )}
          </button>
        </div>

        {/* Action bar and toggles */}
        <div className="composer-actions-row">
          <div className="composer-tools-left">
            <button
              type="button"
              className={`tool-toggle-btn ${searchWeb ? 'active-web' : ''}`}
              onClick={() => setSearchWeb(!searchWeb)}
              title="Search the live web and provide citations"
              id="toggle-web-search"
            >
              🌐 Web Search {searchWeb ? 'ON' : 'OFF'}
            </button>

            <button
              type="button"
              className={`tool-toggle-btn ${emotionalMode ? 'active-emotional' : ''}`}
              onClick={() => setEmotionalMode(!emotionalMode)}
              title="Empathetic, compassionate emotional support mode"
              id="toggle-emotional-mode"
            >
              💖 Emotional Support {emotionalMode ? 'ON' : 'OFF'}
            </button>

            <button
              type="button"
              className={`tool-toggle-btn ${generateTTS ? 'active-web' : ''}`}
              onClick={() => setGenerateTTS(!generateTTS)}
              title="Generate speech audio response (TTS)"
            >
              🔊 Speech TTS {generateTTS ? 'ON' : 'OFF'}
            </button>
          </div>

          <div className="composer-tools-right">
            {/* Hidden file inputs */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              multiple
              accept=".pdf,.txt,.md,.docx,image/*,audio/*"
              style={{ display: 'none' }}
              id="file-input-attachments"
            />
            <input
              type="file"
              ref={audioInputRef}
              onChange={handleAudioTranscribe}
              accept="audio/*"
              style={{ display: 'none' }}
              id="file-input-transcribe"
            />

            <button
              type="button"
              className="btn-icon-composer"
              title="Attach document, image, or audio"
              onClick={() => fileInputRef.current?.click()}
              aria-label="Attach file"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
              </svg>
            </button>

            <button
              type="button"
              className="btn-icon-composer"
              title={isTranscribing ? 'Transcribing...' : 'Upload voice note to transcribe'}
              onClick={() => audioInputRef.current?.click()}
              disabled={isTranscribing}
              aria-label="Voice transcription"
            >
              {isTranscribing ? (
                <div className="spinner" />
              ) : (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                  <line x1="12" y1="19" x2="12" y2="23" />
                  <line x1="8" y1="23" x2="16" y2="23" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
