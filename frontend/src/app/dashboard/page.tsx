"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Bot,
  Brain,
  LogOut,
  Menu,
  MessageSquare,
  Plus,
  Send,
  Trash2,
  User,
} from "lucide-react";

import {
  createConversation,
  createMessage,
  deleteConversation,
  getConversations,
  getMessages,
} from "@/lib/api";

import { clearTokens, getAccessToken } from "@/lib/auth";

import type { Conversation } from "@/types/conversation";
import type { Message } from "@/types/message";

// --------------------------------------------------
// HELPERS
// --------------------------------------------------

function uniqueById<T extends { id: string }>(items: T[]): T[] {
  return Array.from(new Map(items.map((item) => [item.id, item])).values());
}

// --------------------------------------------------
// PAGE
// --------------------------------------------------

export default function DashboardPage() {
  const router = useRouter();

  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<
    string | null
  >(null);

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  const [loading, setLoading] = useState(false);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);

  const [sidebarOpen, setSidebarOpen] = useState(true);

  const [error, setError] = useState<string | null>(null);

  const [authenticated, setAuthenticated] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);

  // --------------------------------------------------
  // AUTHENTICATION
  // --------------------------------------------------

  useEffect(() => {
    const accessToken = getAccessToken();

    if (!accessToken) {
      setAuthChecked(true);
      router.replace("/login");
      return;
    }

    setAuthenticated(true);
    setAuthChecked(true);
  }, [router]);

  // --------------------------------------------------
  // LOAD CONVERSATIONS
  // --------------------------------------------------

  useEffect(() => {
    if (!authenticated) {
      return;
    }

    const accessToken = getAccessToken();

    if (!accessToken) {
      return;
    }

    let cancelled = false;

    async function loadConversations() {
      try {
        setLoadingConversations(true);
        setError(null);

        const data = await getConversations(accessToken);

        if (!cancelled) {
          setConversations(uniqueById(data));
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load conversations.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoadingConversations(false);
        }
      }
    }

    void loadConversations();

    return () => {
      cancelled = true;
    };
  }, [authenticated]);

  // --------------------------------------------------
  // LOAD MESSAGES
  // --------------------------------------------------

  useEffect(() => {
    if (!authenticated) {
      return;
    }

    if (!activeConversationId) {
      setMessages([]);
      setLoadingMessages(false);
      return;
    }

    const accessToken = getAccessToken();

    if (!accessToken) {
      return;
    }

    const conversationId = activeConversationId;

    let cancelled = false;

    async function loadMessages() {
      try {
        setLoadingMessages(true);
        setError(null);

        const data = await getMessages(accessToken, conversationId);

        if (!cancelled) {
          setMessages(uniqueById(data));
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load messages.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoadingMessages(false);
        }
      }
    }

    void loadMessages();

    return () => {
      cancelled = true;
    };
  }, [activeConversationId, authenticated]);

  // --------------------------------------------------
  // NEW CHAT
  // --------------------------------------------------

  function startNewChat() {
    setActiveConversationId(null);
    setMessages([]);
    setInput("");
    setError(null);

    router.push("/dashboard");
  }

  // --------------------------------------------------
  // SEND MESSAGE
  // --------------------------------------------------

  async function handleSend() {
    const content = input.trim();

    if (!content || loading) {
      return;
    }

    const accessToken = getAccessToken();

    if (!accessToken) {
      router.replace("/login");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      let conversationId = activeConversationId;

      // ------------------------------------------------
      // CREATE CONVERSATION AUTOMATICALLY
      // ------------------------------------------------

      if (!conversationId) {
        const title =
          content.length > 50 ? `${content.slice(0, 50)}...` : content;

        const conversation = await createConversation(accessToken, {
          title,
        });

        conversationId = conversation.id;

        setActiveConversationId(conversation.id);

        setConversations((previous) => uniqueById([conversation, ...previous]));
      }

      // ------------------------------------------------
      // SEND MESSAGE
      // ------------------------------------------------

      const pair = await createMessage(accessToken, conversationId, {
        content,
      });

      setMessages((previous) =>
        uniqueById([...previous, pair.user_message, pair.assistant_message]),
      );

      setInput("");

      setTimeout(() => {
        textareaRef.current?.focus();
      }, 50);

      // ------------------------------------------------
      // REFRESH CONVERSATIONS
      // ------------------------------------------------

      const updatedConversations = await getConversations(accessToken);

      setConversations(uniqueById(updatedConversations));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message.");
    } finally {
      setLoading(false);
    }
  }

  // --------------------------------------------------
  // ENTER TO SEND
  // --------------------------------------------------

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handleSend();
    }
  }

  // --------------------------------------------------
  // DELETE CONVERSATION
  // --------------------------------------------------

  async function handleDeleteConversation(conversationId: string) {
    const accessToken = getAccessToken();

    if (!accessToken) {
      router.replace("/login");
      return;
    }

    try {
      setError(null);

      await deleteConversation(accessToken, conversationId);

      setConversations((previous) =>
        previous.filter((conversation) => conversation.id !== conversationId),
      );

      if (activeConversationId === conversationId) {
        setActiveConversationId(null);
        setMessages([]);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to delete conversation.",
      );
    }
  }

  // --------------------------------------------------
  // LOGOUT
  // --------------------------------------------------

  function handleLogout() {
    clearTokens();

    setAuthenticated(false);
    setConversations([]);
    setMessages([]);
    setActiveConversationId(null);

    router.replace("/login");
  }

  // --------------------------------------------------
  // INITIAL LOADING
  // IMPORTANT:
  // Same HTML is rendered initially on server and client.
  // This prevents hydration mismatch.
  // --------------------------------------------------

  if (!authChecked || !authenticated) {
    return (
      <main className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-zinc-400">Loading...</div>
      </main>
    );
  }

  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <main className="h-screen bg-black text-white flex overflow-hidden">
      {/* SIDEBAR */}

      <aside
        className={`${
          sidebarOpen ? "w-72" : "w-0"
        } shrink-0 border-r border-zinc-800 bg-zinc-950 transition-all duration-200 overflow-hidden`}
      >
        <div className="w-72 h-full flex flex-col">
          {/* HEADER */}

          <div className="p-4 border-b border-zinc-800">
            <div className="flex items-center gap-2 mb-4">
              <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
                <Bot size={18} />
              </div>

              <div>
                <div className="font-semibold">AI Digital Twin</div>

                <div className="text-xs text-zinc-500">
                  Personal AI assistant
                </div>
              </div>
            </div>

            <button
              onClick={startNewChat}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-white text-black py-2.5 text-sm font-medium hover:bg-zinc-200 transition"
            >
              <Plus size={17} />
              New chat
            </button>
          </div>

          {/* CONVERSATIONS */}

          <div className="flex-1 overflow-y-auto p-3">
            <div className="text-xs uppercase tracking-wider text-zinc-500 px-2 mb-2">
              Conversations
            </div>

            {loadingConversations ? (
              <div className="text-sm text-zinc-500 px-2 py-4">Loading...</div>
            ) : conversations.length === 0 ? (
              <div className="text-sm text-zinc-500 px-2 py-4">
                No conversations yet.
              </div>
            ) : (
              <div className="space-y-1">
                {conversations.map((conversation) => {
                  const active = conversation.id === activeConversationId;

                  return (
                    <div
                      key={conversation.id}
                      className={`group flex items-center gap-2 rounded-lg px-3 py-2 ${
                        active ? "bg-zinc-800" : "hover:bg-zinc-900"
                      }`}
                    >
                      <button
                        onClick={() => setActiveConversationId(conversation.id)}
                        className="flex-1 min-w-0 text-left"
                      >
                        <div className="flex items-center gap-2">
                          <MessageSquare
                            size={15}
                            className="shrink-0 text-zinc-500"
                          />

                          <span className="truncate text-sm">
                            {conversation.title}
                          </span>
                        </div>
                      </button>

                      <button
                        onClick={() =>
                          void handleDeleteConversation(conversation.id)
                        }
                        className="opacity-0 group-hover:opacity-100 text-zinc-500 hover:text-red-400 transition"
                        title="Delete conversation"
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* FOOTER */}

          <div className="border-t border-zinc-800 p-3 space-y-1">
            <button
              onClick={() => router.push("/memories")}
              className="w-full flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-zinc-400 hover:bg-zinc-900 hover:text-white"
            >
              <Brain size={17} />
              Memories
            </button>

            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-zinc-400 hover:bg-zinc-900 hover:text-white"
            >
              <LogOut size={17} />
              Logout
            </button>
          </div>
        </div>
      </aside>

      {/* MAIN */}

      <section className="flex-1 flex flex-col min-w-0">
        {/* TOP BAR */}

        <header className="h-14 shrink-0 border-b border-zinc-800 flex items-center px-4 gap-3">
          <button
            onClick={() => setSidebarOpen((value) => !value)}
            className="p-2 rounded-lg hover:bg-zinc-900 text-zinc-400"
          >
            <Menu size={20} />
          </button>

          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-md bg-blue-600 flex items-center justify-center">
              <Bot size={15} />
            </div>

            <span className="font-medium">AI Digital Twin</span>
          </div>

          <div className="ml-auto flex items-center gap-2 text-zinc-500">
            <User size={17} />
          </div>
        </header>

        {/* MESSAGES */}

        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-4 py-8">
            {!activeConversationId && messages.length === 0 ? (
              <div className="min-h-[60vh] flex flex-col items-center justify-center text-center">
                <div className="h-16 w-16 rounded-2xl bg-blue-600/15 border border-blue-500/20 flex items-center justify-center mb-6">
                  <Bot size={32} className="text-blue-400" />
                </div>

                <h1 className="text-3xl font-semibold mb-3">
                  What can I help you with?
                </h1>

                <p className="text-zinc-500 max-w-lg">
                  Start a conversation with your Digital Twin. Your first
                  message automatically creates a conversation.
                </p>
              </div>
            ) : loadingMessages ? (
              <div className="text-center text-zinc-500 py-10">
                Loading conversation...
              </div>
            ) : (
              <div className="space-y-6">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    {message.role === "assistant" && (
                      <div className="h-8 w-8 shrink-0 rounded-lg bg-blue-600 flex items-center justify-center">
                        <Bot size={17} />
                      </div>
                    )}

                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-3 whitespace-pre-wrap leading-7 ${
                        message.role === "user"
                          ? "bg-blue-600 text-white"
                          : "bg-zinc-900 border border-zinc-800 text-zinc-200"
                      }`}
                    >
                      {message.content}
                    </div>

                    {message.role === "user" && (
                      <div className="h-8 w-8 shrink-0 rounded-lg bg-zinc-800 flex items-center justify-center">
                        <User size={17} />
                      </div>
                    )}
                  </div>
                ))}

                {loading && (
                  <div className="flex gap-3">
                    <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
                      <Bot size={17} />
                    </div>

                    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl px-4 py-3 text-zinc-500">
                      Thinking...
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* ERROR */}

        {error && (
          <div className="max-w-4xl w-full mx-auto px-4 pb-2">
            <div className="rounded-lg border border-red-900 bg-red-950/40 px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          </div>
        )}

        {/* INPUT */}

        <div className="shrink-0 border-t border-zinc-800 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end gap-2 rounded-2xl border border-zinc-700 bg-zinc-900 p-2 focus-within:border-zinc-500">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Message your Digital Twin..."
                rows={1}
                disabled={loading}
                className="flex-1 resize-none bg-transparent px-3 py-2.5 outline-none text-sm text-white placeholder:text-zinc-500 max-h-40"
              />

              <button
                onClick={() => void handleSend()}
                disabled={loading || !input.trim()}
                className="h-10 w-10 shrink-0 rounded-xl bg-blue-600 flex items-center justify-center hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed transition"
              >
                <Send size={18} />
              </button>
            </div>

            <div className="text-center text-xs text-zinc-600 mt-2">
              Enter to send · Shift + Enter for new line
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
