"use client";

import { CheckCircle2, Clock3, PhoneCall, PhoneMissed } from "lucide-react";
import { useEffect, useState } from "react";

import { getRecentCalls } from "@/lib/api/dashboard";
import type { RecentCallItem } from "@/lib/api/types";

function formatDuration(seconds: number | null) {
  if (seconds === null) return "—";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
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
    <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-500">
      <Clock3 className="h-3.5 w-3.5" />
      {outcome ?? "In progress"}
    </span>
  );
}

export default function CallHistoryPage() {
  const [calls, setCalls] = useState<RecentCallItem[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getRecentCalls(100)
      .then(setCalls)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Failed to load calls."),
      );
  }, []);

  return (
    <div className="space-y-5">
      <p className="text-sm text-slate-400">
        {calls ? `${calls.length} calls` : ""}
      </p>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
        {error ? (
          <div className="p-6 text-sm text-red-700">{error}</div>
        ) : calls === null ? (
          <div className="p-10 text-center text-sm text-slate-400">
            Loading…
          </div>
        ) : calls.length === 0 ? (
          <div className="p-10 text-center text-sm text-slate-400">
            No calls logged yet.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {calls.map((call) => (
              <div
                key={call.id}
                className="flex items-center gap-4 px-5 py-4 hover:bg-slate-50/60"
              >
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#0D9488]/10 text-[#0D9488]">
                  <PhoneCall className="h-4 w-4" />
                </div>

                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-slate-900">
                    {call.patient_name ?? call.caller_phone}
                  </p>
                  <p className="mt-0.5 truncate text-xs text-slate-400">
                    {call.intent ?? "General inquiry"} · {call.caller_phone}
                  </p>
                </div>

                <div className="hidden shrink-0 text-right text-xs text-slate-400 sm:block">
                  <p>{formatDuration(call.duration_seconds)}</p>
                  <p className="mt-0.5">
                    {new Date(call.started_at).toLocaleString()}
                  </p>
                </div>

                <OutcomeBadge outcome={call.outcome} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
