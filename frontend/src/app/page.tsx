import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-zinc-950 px-6 text-white">
      <section className="w-full max-w-3xl text-center">
        <p className="mb-4 text-sm font-medium uppercase tracking-[0.25em] text-zinc-400">
          AI Digital Twin
        </p>

        <h1 className="text-5xl font-semibold tracking-tight sm:text-6xl">
          Your AI that remembers.
        </h1>

        <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-zinc-400">
          A personal AI assistant with conversations, long-term memory,
          authentication, and an extensible AI backend.
        </p>

        <div className="mt-10 flex flex-col justify-center gap-4 sm:flex-row">
          <Link
            href="/login"
            className="rounded-xl bg-white px-6 py-3 font-medium text-zinc-950 transition hover:bg-zinc-200"
          >
            Sign in
          </Link>

          <Link
            href="/register"
            className="rounded-xl border border-zinc-700 px-6 py-3 font-medium text-white transition hover:bg-zinc-900"
          >
            Create account
          </Link>
        </div>
      </section>
    </main>
  );
}