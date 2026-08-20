"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { deleteMemory, getMemories } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import type { Memory } from "@/types/memory";

export default function MemoriesPage() {
  const router = useRouter();

  const [memories, setMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadMemories() {
      const token = getAccessToken();

      if (!token) {
        router.replace("/login");
        return;
      }

      try {
        const data = await getMemories(token);
        setMemories(data);
      } catch (error) {
        setError(
          error instanceof Error ? error.message : "Unable to load memories.",
        );
      } finally {
        setLoading(false);
      }
    }

    void loadMemories();
  }, [router]);

  async function handleDelete(memoryId: string) {
    const token = getAccessToken();

    if (!token) {
      router.replace("/login");
      return;
    }

    const confirmed = window.confirm("Delete this memory permanently?");

    if (!confirmed) {
      return;
    }

    try {
      await deleteMemory(token, memoryId);

      setMemories((current) =>
        current.filter((memory) => memory.id !== memoryId),
      );
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Unable to delete memory.",
      );
    }
  }

  return (
    <main className="min-h-screen bg-zinc-950 text-white">
      <header className="border-b border-zinc-800">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <div>
            <Link
              href="/"
              className="text-sm text-zinc-500 hover:text-zinc-300"
            >
              ← Dashboard
            </Link>

            <h1 className="mt-1 text-xl font-semibold">Long-term memories</h1>
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-5xl px-6 py-10">
        <div className="mb-8">
          <h2 className="text-3xl font-semibold">
            What your Digital Twin remembers
          </h2>

          <p className="mt-2 text-zinc-500">
            These are explicit pieces of information saved from your
            conversations.
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-lg border border-red-900 bg-red-950/40 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        {loading ? (
          <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-8 text-center text-zinc-500">
            Loading memories...
          </div>
        ) : memories.length === 0 ? (
          <div className="rounded-xl border border-dashed border-zinc-800 bg-zinc-900/40 p-12 text-center">
            <h3 className="text-lg font-medium">No memories yet</h3>

            <p className="mt-2 text-sm text-zinc-500">
              Tell your Digital Twin something about yourself during a
              conversation.
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {memories.map((memory) => (
              <article
                key={memory.id}
                className="rounded-xl border border-zinc-800 bg-zinc-900 p-5"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <span className="inline-block rounded-full bg-blue-950 px-3 py-1 text-xs font-medium text-blue-300">
                      {memory.memory_type}
                    </span>

                    <h3 className="mt-3 text-lg font-medium">{memory.key}</h3>

                    <p className="mt-2 break-words text-zinc-300">
                      {memory.value}
                    </p>

                    <p className="mt-3 text-xs text-zinc-600">
                      Updated {new Date(memory.updated_at).toLocaleString()}
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => void handleDelete(memory.id)}
                    className="shrink-0 rounded-lg px-3 py-2 text-sm text-red-400 transition hover:bg-red-950/40"
                  >
                    Delete
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
