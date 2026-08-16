"use client";

import {
  CheckCircle2,
  Clock3,
  PhoneCall,
  PhoneMissed,
} from "lucide-react";
import { useEffect, useState } from "react";

import { getRecentCalls } from "@/lib/api/dashboard";
import type { RecentCallItem } from "@/lib/api/types";

function formatDuration(seconds: number | null) {
  if (seconds === null) return "—";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function timeAgo(iso: string) {
  const diffMs = Date.now() - new Date(iso).getTime();
  const minutes = Math.round(diffMs / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours} hr ago`;
  return new Date(iso).toLocaleDateString();
}

function OutcomeBadge({ outcome }: { outcome: string | null }) {
  if (outcome === "Resolved") {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
        <CheckCircle2 className="h-3.5 w-3.5" />
        Resolved
      </span>
    );
  }

  if (outcome === "Escalated to Human" || outcome === "Failed") {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700">
        <PhoneMissed className="h-3.5 w-3.5" />
        {outcome}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground">
      <Clock3 className="h-3.5 w-3.5" />
      {outcome ?? "In progress"}
    </span>
  );
}

export function RecentAgentConversation() {
  const [calls, setCalls] = useState<RecentCallItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getRecentCalls(5)
      .then(setCalls)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Failed to load calls."),
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="rounded-xl border bg-white">
      <div className="flex items-center justify-between border-b px-5 py-4">
        <div>
          <h2 className="text-sm font-semibold">Recent AI Conversations</h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Latest voice-agent interactions
          </p>
        </div>
      </div>

      {error && <div className="px-5 py-4 text-sm text-red-700">{error}</div>}

      <div className="divide-y">
        {loading ? (
          <div className="px-5 py-8 text-center text-sm text-muted-foreground">
            Loading…
          </div>
        ) : calls.length === 0 ? (
          <div className="px-5 py-8 text-center text-sm text-muted-foreground">
            No calls logged yet.
          </div>
        ) : (
          calls.map((call) => (
            <div
              key={call.id}
              className="flex items-center gap-4 px-5 py-4 transition-colors hover:bg-muted/30"
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                <PhoneCall className="h-4 w-4" />
              </div>

              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="truncate text-sm font-medium">
                    {call.patient_name ?? call.caller_phone}
                  </p>
                  <span className="hidden rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground sm:inline-flex">
                    AI Voice
                  </span>
                </div>
                <p className="mt-1 truncate text-xs font-medium">
                  {call.intent ?? "General inquiry"}
                </p>
              </div>

              <div className="hidden shrink-0 text-right md:block">
                <div className="flex items-center justify-end gap-1.5 text-xs text-muted-foreground">
                  <Clock3 className="h-3.5 w-3.5" />
                  {formatDuration(call.duration_seconds)}
                </div>
                <p className="mt-1 text-[11px] text-muted-foreground">
                  {timeAgo(call.started_at)}
                </p>
              </div>

              <div className="hidden sm:block">
                <OutcomeBadge outcome={call.outcome} />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
