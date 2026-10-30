import React, { useState, useEffect } from 'react';
import { Conversation, Message, AttachmentItem } from './types';
import { api } from './services/api';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { ChatArea } from './components/ChatArea';
import { Composer } from './components/Composer';
import { DocumentWorkspace } from './components/DocumentWorkspace';
import './App.css';

export const App: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [activeTitle, setActiveTitle] = useState('New Conversation');
  const [messages, setMessages] = useState<Message[]>([]);
  const [documentCount, setDocumentCount] = useState<number>(0);
  const [isWorkspaceOpen, setIsWorkspaceOpen] = useState(false);
  const [isSidebarMobileOpen, setIsSidebarMobileOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Initial loads
  const loadConversations = async () => {
    try {
      const data = await api.getConversations();
      setConversations(data);
    } catch (err: any) {
      console.error('Failed to load conversations:', err);
    }
  };

  const loadDocumentsCount = async () => {
    try {
      const docs = await api.listDocuments();
      setDocumentCount(docs.length);
    } catch (err: any) {
      console.error('Failed to count documents:', err);
    }
  };

  useEffect(() => {
    loadConversations();
    loadDocumentsCount();
  }, []);

  const selectConversation = async (id: number) => {
    setActiveConversationId(id);
    setIsSidebarMobileOpen(false);
    setErrorMessage(null);
    try {
      const detail = await api.getConversation(id);
      setActiveTitle(detail.title);
      setMessages(detail.messages || []);
    } catch (err: any) {
      setErrorMessage(`Failed to load conversation: ${err.message}`);
    }
  };

  const handleNewChat = () => {
    setActiveConversationId(null);
    setActiveTitle('New Conversation');
    setMessages([]);
    setIsSidebarMobileOpen(false);
    setErrorMessage(null);
  };

  const handleDeleteConversation = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Delete this conversation?')) return;

    try {
      await api.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConversationId === id) {
        handleNewChat();
      }
    } catch (err: any) {
      setErrorMessage(`Failed to delete conversation: ${err.message}`);
    }
  };

  const handleSendMessage = async (params: {
    message: string;
    search_web: boolean;
    emotional_mode: boolean;
    generate_tts: boolean;
    generate_image: boolean;
    attachments: AttachmentItem[];
  }) => {
    setErrorMessage(null);

    // Optimistic local user message
    const tempUserMsg: Message = {
      id: Date.now(),
      conversation_id: activeConversationId || 0,
      sender: 'user',
      text: params.message,
      meta: {
        attachments: params.attachments.map((a) => a.filename),
        emotional_mode: params.emotional_mode,
        search_web: params.search_web,
      },
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setIsLoading(true);

    try {
      const res = await api.sendChatMessage({
        message: params.message,
        conversation_id: activeConversationId || undefined,
        search_web: params.search_web,
        emotional_mode: params.emotional_mode,
        generate_tts: params.generate_tts,
        generate_image: params.generate_image,
        attachments: params.attachments,
      });

      // If this was a new conversation, update active ID and list
      if (!activeConversationId) {
        setActiveConversationId(res.conversation_id);
        await loadConversations();
      }

      // Add assistant response to messages
      const asstMsg: Message = {
        id: res.message_id,
        conversation_id: res.conversation_id,
        sender: 'assistant',
        text: res.reply,
        meta: {
          citations: res.citations,
          audio_url: res.audio_url,
          generated_image_url: res.generated_image_url,
          emotional_mode: res.emotional_mode_active,
        },
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, asstMsg]);
    } catch (err: any) {
      setErrorMessage(`AI Error: ${err.message}`);
      // Remove optimistic message on failure if desired or keep with error flag
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar for conversations */}
      <Sidebar
        conversations={conversations}
        activeId={activeConversationId}
        onSelect={selectConversation}
        onNewChat={handleNewChat}
        onDelete={handleDeleteConversation}
        isOpen={isSidebarMobileOpen}
        onCloseMobile={() => setIsSidebarMobileOpen(false)}
      />

      {/* Main chat viewport */}
      <main className="main-chat">
        <Header
          title={activeTitle}
          isEmotionalMode={messages.some((m) => m.meta?.emotional_mode)}
          isWebSearch={messages.some((m) => m.meta?.search_web)}
          documentCount={documentCount}
          onOpenWorkspace={() => setIsWorkspaceOpen(true)}
          onToggleSidebarMobile={() => setIsSidebarMobileOpen(!isSidebarMobileOpen)}
        />

        {/* Global friendly error alert */}
        {errorMessage && (
          <div
            style={{
              margin: '12px 24px 0',
              padding: '10px 16px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--danger-bg)',
              color: 'var(--danger)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              fontSize: '0.86rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <span>⚠️ {errorMessage}</span>
            <button
              onClick={() => setErrorMessage(null)}
              style={{ background: 'transparent', border: 'none', color: 'var(--danger)', cursor: 'pointer' }}
            >
              ✕
            </button>
          </div>
        )}

        <ChatArea
          messages={messages}
          isLoading={isLoading}
          onSelectPrompt={(prompt, opts) => {
            handleSendMessage({
              message: prompt,
              search_web: !!opts?.search_web,
              emotional_mode: !!opts?.emotional_mode,
              generate_tts: false,
              generate_image: !!opts?.generate_image,
              attachments: [],
            });
          }}
        />

        <Composer
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </main>

      {/* Document Workspace Slide-over */}
      <DocumentWorkspace
        isOpen={isWorkspaceOpen}
        onClose={() => setIsWorkspaceOpen(false)}
        onDocumentsChanged={loadDocumentsCount}
      />
    </div>
  );
};

export default App;
