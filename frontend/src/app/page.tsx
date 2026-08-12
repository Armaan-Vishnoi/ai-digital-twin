"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import {
  createConversation,
  deleteConversation,
  getConversations,
  getCurrentUser,
} from "@/lib/api";
import {
  clearTokens,
  getAccessToken,
} from "@/lib/auth";
import type { Conversation } from "@/types/conversation";
import type { UserResponse } from "@/types/auth";

export default function Home() {
  const router = useRouter();

  const [user, setUser] = useState<UserResponse | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);

  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      const token = getAccessToken();

      if (!token) {
        router.replace("/login");
        return;
      }

      try {
        const [currentUser, userConversations] = await Promise.all([
          getCurrentUser(token),
          getConversations(token),
        ]);

        setUser(currentUser);
        setConversations(userConversations);
      } catch (error) {
        clearTokens();

        setError(
          error instanceof Error
            ? error.message
            : "Unable to load dashboard.",
        );

        router.replace("/login");
      } finally {
        setLoading(false);
      }
    }

    void loadDashboard();
  }, [router]);

  async function handleCreateConversation() {
    const token = getAccessToken();

    if (!token) {
      router.replace("/login");
      return;
    }

    const title = window.prompt("Conversation title:");

    if (!title?.trim()) {
      return;
    }

    setCreating(true);
    setError("");

    try {
      const conversation = await createConversation(token, {
        title: title.trim(),
      });

      setConversations((current) => [
        conversation,
        ...current,
      ]);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Unable to create conversation.",
      );
    } finally {
      setCreating(false);
    }
  }

  async function handleDeleteConversation(
    conversationId: string,
  ) {
    const token = getAccessToken();

    if (!token) {
      router.replace("/login");
      return;
    }

    const confirmed = window.confirm(
      "Delete this conversation?",
    );

    if (!confirmed) {
      return;
    }

    try {
      await deleteConversation(token, conversationId);

      setConversations((current) =>
        current.filter(
          (conversation) => conversation.id !== conversationId,
        ),
      );
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Unable to delete conversation.",
      );
    }
  }

  function handleLogout() {
    clearTokens();
    router.replace("/login");
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-zinc-950 text-zinc-400">
        Loading your digital twin...
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-zinc-950 text-white">
      <header className="border-b border-zinc-800">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <p className="text-sm font-medium text-blue-400">
              AI Digital Twin
            </p>

            <h1 className="text-xl font-semibold">
              Dashboard
            </h1>
          </div>

          <button
            type="button"
            onClick={handleLogout}
            className="rounded-lg border border-zinc-700 px-4 py-2 text-sm text-zinc-300 transition hover:bg-zinc-800"
          >
            Log out
          </button>
        </div>
      </header>

      <section className="mx-auto max-w-7xl px-6 py-10">
        <div className="mb-10">
          <p className="text-sm text-zinc-400">
            Welcome back
          </p>

          <h2 className="mt-1 text-3xl font-semibold">
            {user?.full_name}
          </h2>

          <p className="mt-2 text-zinc-500">
            {user?.email}
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-lg border border-red-900 bg-red-950/40 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        <div className="mb-6 flex items-center justify-between">
          <div>
            <h3 className="text-xl font-semibold">
              Conversations
            </h3>

            <p className="mt-1 text-sm text-zinc-500">
              Your private conversations with your digital twin.
            </p>
          </div>

          <button
            type="button"
            onClick={handleCreateConversation}
            disabled={creating}
            className="rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {creating
              ? "Creating..."
              : "+ New conversation"}
          </button>
        </div>

        {conversations.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-zinc-800 bg-zinc-900/40 px-6 py-16 text-center">
            <h4 className="text-lg font-medium">
              No conversations yet
            </h4>

            <p className="mt-2 text-sm text-zinc-500">
              Create your first conversation with your digital twin.
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                className="flex items-center justify-between rounded-xl border border-zinc-800 bg-zinc-900 p-5"
              >
                <Link
                  href={`/chat/${conversation.id}`}
                  className="min-w-0 flex-1"
                >
                  <h4 className="truncate font-medium text-white hover:text-blue-400">
                    {conversation.title}
                  </h4>

                  <p className="mt-1 text-xs text-zinc-500">
                    Updated{" "}
                    {new Date(
                      conversation.updated_at,
                    ).toLocaleString()}
                  </p>
                </Link>

                <button
                  type="button"
                  onClick={() =>
                    void handleDeleteConversation(
                      conversation.id,
                    )
                  }
                  className="ml-4 rounded-lg px-3 py-2 text-sm text-red-400 transition hover:bg-red-950/40"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}