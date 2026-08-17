"use client";

import {
  Activity,
  CalendarCheck,
  PhoneCall,
  UserPlus,
} from "lucide-react";
import { useEffect, useState } from "react";

import { getActivityLogs } from "@/lib/api/activity-logs";
import type { ActivityLog } from "@/lib/api/activity-logs";

function iconFor(eventType: string) {
  const type = eventType.toLowerCase();
  if (type.includes("appointment")) return CalendarCheck;
  if (type.includes("call")) return PhoneCall;
  if (type.includes("patient")) return UserPlus;
  return Activity;
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

export function ActivityLogCard() {
  const [logs, setLogs] = useState<ActivityLog[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getActivityLogs(10)
      .then(setLogs)
      .catch((err) =>
        setError(
          err instanceof Error ? err.message : "Failed to load activity.",
        ),
      );
  }, []);

  return (
    <div className="rounded-xl border border-slate-200 bg-white">
      <div className="border-b border-slate-200 px-5 py-4">
        <h2 className="text-sm font-semibold text-slate-900">
          Recent Activity
        </h2>
        <p className="mt-0.5 text-xs text-slate-400">
          System-wide event log
        </p>
      </div>

      {error && <div className="px-5 py-4 text-sm text-red-700">{error}</div>}

      <div className="divide-y divide-slate-100">
        {logs === null ? (
          <div className="px-5 py-8 text-center text-sm text-slate-400">
            Loading…
          </div>
        ) : logs.length === 0 ? (
          <div className="px-5 py-8 text-center text-sm text-slate-400">
            No recent activity.
          </div>
        ) : (
          logs.map((log) => {
            const Icon = iconFor(log.event_type);
            return (
              <div key={log.id} className="flex items-start gap-3 px-5 py-3">
                <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#0D9488]/10 text-[#0D9488]">
                  <Icon className="h-3.5 w-3.5" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm text-slate-700">
                    {log.description ?? log.event_type}
                  </p>
                  <p className="mt-0.5 text-xs text-slate-400">
                    {log.actor_type} · {timeAgo(log.created_at)}
                  </p>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
