"use client";

import { FormEvent, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

import {
  createMessage,
  getConversation,
  getMessages,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import type { Conversation } from "@/types/conversation";
import type { Message } from "@/types/message";

export default function ChatPage() {
  const params = useParams();
  const router = useRouter();

  const conversationId = params.conversationId as string;

  const [conversation, setConversation] =
    useState<Conversation | null>(null);

  const [messages, setMessages] = useState<Message[]>([]);
  const [content, setContent] = useState("");

  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadChat() {
      const token = getAccessToken();

      if (!token) {
        router.replace("/login");
        return;
      }

      try {
        const [conversationData, messageData] =
          await Promise.all([
            getConversation(token, conversationId),
            getMessages(token, conversationId),
          ]);

        setConversation(conversationData);
        setMessages(messageData);
      } catch (error) {
        setError(
          error instanceof Error
            ? error.message
            : "Unable to load conversation.",
        );
      } finally {
        setLoading(false);
      }
    }

    void loadChat();
  }, [conversationId, router]);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const token = getAccessToken();

    if (!token) {
      router.replace("/login");
      return;
    }

    const trimmedContent = content.trim();

    if (!trimmedContent || sending) {
      return;
    }

    setSending(true);
    setError("");

    try {
      const response = await createMessage(
        token,
        conversationId,
        {
          content: trimmedContent,
        },
      );

      setMessages((current) => [
        ...current,
        response.user_message,
        response.assistant_message,
      ]);

      setContent("");
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Unable to send message.",
      );
    } finally {
      setSending(false);
    }
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-zinc-950 text-zinc-400">
        Loading conversation...
      </main>
    );
  }

  if (!conversation) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-zinc-950 px-6">
        <div className="text-center">
          <h1 className="text-xl font-semibold text-white">
            Conversation not found
          </h1>

          <Link
            href="/"
            className="mt-4 inline-block text-blue-400 hover:text-blue-300"
          >
            Back to dashboard
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col bg-zinc-950 text-white">
      {/* Header */}

      <header className="border-b border-zinc-800">
        <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-4">
          <div className="min-w-0">
            <Link
              href="/"
              className="text-sm text-zinc-500 hover:text-zinc-300"
            >
              ← Dashboard
            </Link>

            <h1 className="mt-1 truncate text-lg font-semibold">
              {conversation.title}
            </h1>
          </div>
        </div>
      </header>

      {/* Messages */}

      <section className="flex-1 overflow-y-auto">
        <div className="mx-auto w-full max-w-5xl px-6 py-8">
          {messages.length === 0 ? (
            <div className="flex min-h-[50vh] items-center justify-center">
              <div className="text-center">
                <h2 className="text-2xl font-semibold">
                  Start the conversation
                </h2>

                <p className="mt-2 text-zinc-500">
                  Talk to your AI Digital Twin.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message) => {
                const isUser = message.role === "user";

                return (
                  <div
                    key={message.id}
                    className={`flex ${
                      isUser
                        ? "justify-end"
                        : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                        isUser
                          ? "bg-blue-600 text-white"
                          : "border border-zinc-800 bg-zinc-900 text-zinc-100"
                      }`}
                    >
                      <p className="whitespace-pre-wrap leading-7">
                        {message.content}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {error && (
            <div className="mt-6 rounded-lg border border-red-900 bg-red-950/40 px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          )}
        </div>
      </section>

      {/* Composer */}

      <footer className="border-t border-zinc-800 bg-zinc-950">
        <form
          onSubmit={handleSubmit}
          className="mx-auto flex w-full max-w-5xl gap-3 px-6 py-5"
        >
          <input
            type="text"
            value={content}
            onChange={(event) =>
              setContent(event.target.value)
            }
            disabled={sending}
            placeholder="Message your digital twin..."
            className="min-w-0 flex-1 rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-3 text-white outline-none placeholder:text-zinc-600 focus:border-blue-500 disabled:opacity-60"
          />

          <button
            type="submit"
            disabled={sending || !content.trim()}
            className="rounded-xl bg-blue-600 px-6 py-3 font-medium transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {sending ? "..." : "Send"}
          </button>
        </form>
      </footer>
    </main>
  );
}