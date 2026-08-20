import type { TokenResponse, UserRegister, UserResponse } from "@/types/auth";
import type { Memory } from "@/types/memory";
import type { Conversation, ConversationCreate } from "@/types/conversation";
import type { Message, MessageCreate, MessagePair } from "@/types/message";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

async function parseResponse<T>(response: Response): Promise<T> {
  const data: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    if (
      typeof data === "object" &&
      data !== null &&
      "detail" in data &&
      typeof data.detail === "string"
    ) {
      throw new Error(data.detail);
    }

    throw new Error(`Request failed with status ${response.status}`);
  }

  return data as T;
}

// --------------------------------------------------
// AUTH
// --------------------------------------------------

export async function registerUser(data: UserRegister): Promise<UserResponse> {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return parseResponse<UserResponse>(response);
}

export async function loginUser(
  email: string,
  password: string,
): Promise<TokenResponse> {
  const body = new URLSearchParams();

  body.set("username", email);
  body.set("password", password);

  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: body.toString(),
  });

  return parseResponse<TokenResponse>(response);
}

export async function getCurrentUser(
  accessToken: string,
): Promise<UserResponse> {
  const response = await fetch(`${API_URL}/users/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return parseResponse<UserResponse>(response);
}

// --------------------------------------------------
// CONVERSATIONS
// --------------------------------------------------

export async function getConversations(
  accessToken: string,
): Promise<Conversation[]> {
  const response = await fetch(`${API_URL}/conversations`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return parseResponse<Conversation[]>(response);
}

export async function createConversation(
  accessToken: string,
  data: ConversationCreate,
): Promise<Conversation> {
  const response = await fetch(`${API_URL}/conversations`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return parseResponse<Conversation>(response);
}

export async function getConversation(
  accessToken: string,
  conversationId: string,
): Promise<Conversation> {
  const response = await fetch(`${API_URL}/conversations/${conversationId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return parseResponse<Conversation>(response);
}

export async function deleteConversation(
  accessToken: string,
  conversationId: string,
): Promise<void> {
  const response = await fetch(`${API_URL}/conversations/${conversationId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    await parseResponse<unknown>(response);
  }
}

// --------------------------------------------------
// MESSAGES
// --------------------------------------------------

export async function getMessages(
  accessToken: string,
  conversationId: string,
): Promise<Message[]> {
  const response = await fetch(`${API_URL}/messages/${conversationId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return parseResponse<Message[]>(response);
}

export async function createMessage(
  accessToken: string,
  conversationId: string,
  data: MessageCreate,
): Promise<MessagePair> {
  const response = await fetch(`${API_URL}/messages/${conversationId}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return parseResponse<MessagePair>(response);
}

export async function deleteMessage(
  accessToken: string,
  messageId: string,
): Promise<void> {
  const response = await fetch(`${API_URL}/messages/${messageId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    await parseResponse<unknown>(response);
  }
}

// --------------------------------------------------
// MEMORIES
// --------------------------------------------------

export async function getMemories(accessToken: string): Promise<Memory[]> {
  const response = await fetch(`${API_URL}/memories`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return parseResponse<Memory[]>(response);
}

export async function getMemory(
  accessToken: string,
  memoryId: string,
): Promise<Memory> {
  const response = await fetch(`${API_URL}/memories/${memoryId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return parseResponse<Memory>(response);
}

export async function deleteMemory(
  accessToken: string,
  memoryId: string,
): Promise<void> {
  const response = await fetch(`${API_URL}/memories/${memoryId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    await parseResponse<unknown>(response);
  }
}
