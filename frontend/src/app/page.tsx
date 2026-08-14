"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { getAccessToken } from "@/lib/auth";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const token = getAccessToken();

    if (token) {
      router.replace("/dashboard");
    } else {
      router.replace("/login");
    }
  }, [router]);

  return (
    <main className="min-h-screen bg-black text-white flex items-center justify-center">
      <p className="text-zinc-500">
        Loading AI Digital Twin...
      </p>
    </main>
  );
}