export interface MessageCreate {
  content: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  created_at: string;
}

export interface MessagePair {
  user_message: Message;
  assistant_message: Message;
}
