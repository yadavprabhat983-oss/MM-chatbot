export interface AttachmentItem {
  type: 'image' | 'audio' | 'document';
  filename: string;
  content_base64?: string;
  mime_type?: string;
  url?: string;
}

export interface SourceCitation {
  title: string;
  url?: string;
  doc_id?: number;
  chunk_index?: number;
  snippet: string;
  source_type: 'document' | 'web';
}

export interface Message {
  id: number;
  conversation_id: number;
  sender: 'user' | 'assistant' | 'system';
  text: string;
  meta?: {
    attachments?: string[];
    citations?: SourceCitation[];
    audio_url?: string;
    generated_image_url?: string;
    emotional_mode?: boolean;
    search_web?: boolean;
    safety_response?: boolean;
    crisis_resources_provided?: boolean;
    [key: string]: any;
  };
  created_at: string;
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}

export interface DocumentVersion {
  id: number;
  version_number: number;
  content_text: string;
  change_summary?: string;
  created_at: string;
}

export interface DocumentItem {
  id: number;
  title: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: 'indexing' | 'indexed' | 'failed';
  error_message?: string;
  created_at: string;
  updated_at: string;
  chunk_count: number;
}

export interface DocumentDetail extends DocumentItem {
  content_text: string;
  versions: DocumentVersion[];
}

export interface DocumentAIEditResponse {
  original_text: string;
  proposed_text: string;
  diff_summary: string;
}

export interface ChatResponse {
  conversation_id: number;
  message_id: number;
  reply: string;
  citations: SourceCitation[];
  audio_url?: string;
  generated_image_url?: string;
  emotional_mode_active: boolean;
  attachments_processed: string[];
}
