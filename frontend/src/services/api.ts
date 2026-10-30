import {
  Conversation,
  ConversationDetail,
  DocumentItem,
  DocumentDetail,
  DocumentAIEditResponse,
  ChatResponse,
  AttachmentItem
} from '../types';

const API_BASE = '/api';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `Request failed with status ${res.status}`;
    try {
      const errJson = await res.json();
      if (errJson.detail) {
        errorDetail = errJson.detail;
      }
    } catch {
      // ignore json parse error
    }
    throw new Error(errorDetail);
  }
  if (res.status === 204) {
    return {} as T;
  }
  return res.json();
}

export const api = {
  // Health
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse<{ status: string; app_env: string; timestamp: string }>(res);
  },

  // Conversations
  async getConversations(): Promise<Conversation[]> {
    const res = await fetch(`${API_BASE}/conversations`);
    return handleResponse<Conversation[]>(res);
  },

  async createConversation(title?: string): Promise<Conversation> {
    const res = await fetch(`${API_BASE}/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: title || 'New Conversation' }),
    });
    return handleResponse<Conversation>(res);
  },

  async getConversation(id: number): Promise<ConversationDetail> {
    const res = await fetch(`${API_BASE}/conversations/${id}`);
    return handleResponse<ConversationDetail>(res);
  },

  async deleteConversation(id: number): Promise<void> {
    const res = await fetch(`${API_BASE}/conversations/${id}`, {
      method: 'DELETE',
    });
    return handleResponse<void>(res);
  },

  // Chat
  async sendChatMessage(params: {
    message: string;
    conversation_id?: number;
    search_web?: boolean;
    emotional_mode?: boolean;
    generate_tts?: boolean;
    generate_image?: boolean;
    attachments?: AttachmentItem[];
  }): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: params.message,
        conversation_id: params.conversation_id,
        search_web: !!params.search_web,
        emotional_mode: !!params.emotional_mode,
        generate_tts: !!params.generate_tts,
        generate_image: !!params.generate_image,
        attachments: params.attachments || [],
      }),
    });
    return handleResponse<ChatResponse>(res);
  },

  async transcribeAudio(file: File): Promise<{ filename: string; transcription: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/chat/transcribe`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<{ filename: string; transcription: string }>(res);
  },

  // Documents
  async listDocuments(): Promise<DocumentItem[]> {
    const res = await fetch(`${API_BASE}/documents`);
    return handleResponse<DocumentItem[]>(res);
  },

  async uploadDocument(file: File, title?: string): Promise<DocumentItem> {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<DocumentItem>(res);
  },

  async createDocument(title: string, content_text: string): Promise<DocumentItem> {
    const res = await fetch(`${API_BASE}/documents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content_text }),
    });
    return handleResponse<DocumentItem>(res);
  },

  async getDocument(id: number): Promise<DocumentDetail> {
    const res = await fetch(`${API_BASE}/documents/${id}`);
    return handleResponse<DocumentDetail>(res);
  },

  async updateDocument(
    id: number,
    content_text: string,
    title?: string,
    change_summary?: string
  ): Promise<DocumentDetail> {
    const res = await fetch(`${API_BASE}/documents/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content_text, change_summary }),
    });
    return handleResponse<DocumentDetail>(res);
  },

  async aiEditDocument(
    id: number,
    action: string,
    instruction: string
  ): Promise<DocumentAIEditResponse> {
    const res = await fetch(`${API_BASE}/documents/${id}/ai-edit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, instruction }),
    });
    return handleResponse<DocumentAIEditResponse>(res);
  },

  async reindexDocument(id: number): Promise<{ message: string; chunk_count: number }> {
    const res = await fetch(`${API_BASE}/documents/${id}/reindex`, {
      method: 'POST',
    });
    return handleResponse<{ message: string; chunk_count: number }>(res);
  },

  async deleteDocument(id: number): Promise<void> {
    const res = await fetch(`${API_BASE}/documents/${id}`, {
      method: 'DELETE',
    });
    return handleResponse<void>(res);
  },

  getDownloadUrl(id: number, format: 'md' | 'txt' = 'md'): string {
    return `${API_BASE}/documents/${id}/download?format=${format}`;
  },
};
