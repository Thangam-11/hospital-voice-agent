"use client";

import { CalendarDays, Clock3, PhoneCall, Users } from "lucide-react";
import { useEffect, useState } from "react";

import { getDashboardStats } from "@/lib/api/dashboard";
import type { DashboardStats } from "@/lib/api/types";

const CARD_DEFS = [
  {
    key: "total_patients" as const,
    title: "Total Patients",
    description: "registered patients",
    icon: Users,
  },
  {
    key: "appointments_today" as const,
    title: "Appointments Today",
    description: "scheduled for today",
    icon: CalendarDays,
  },
  {
    key: "upcoming_appointments" as const,
    title: "Upcoming Appointments",
    description: "not yet completed",
    icon: Clock3,
  },
  {
    key: "ai_calls_today" as const,
    title: "AI Calls Today",
    description: "handled by the voice agent",
    icon: PhoneCall,
  },
];

export function StatCards() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getDashboardStats()
      .then(setStats)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Failed to load stats."),
      );
  }, []);

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        {error}
      </div>
    );
  }

  return (
    <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
      {CARD_DEFS.map((card) => {
        const Icon = card.icon;
        const value = stats ? stats[card.key] : null;

        return (
          <div
            key={card.key}
            className="rounded-xl border border-slate-200 bg-white p-5 transition-shadow hover:shadow-sm"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-[13px] font-medium text-slate-500">
                  {card.title}
                </p>

                <p className="mt-2 text-[26px] font-semibold tracking-tight text-slate-900">
                  {value === null ? (
                    <span className="inline-block h-7 w-14 animate-pulse rounded bg-slate-100" />
                  ) : (
                    value.toLocaleString()
                  )}
                </p>
              </div>

              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#0D9488]/10 text-[#0D9488]">
                <Icon className="h-[18px] w-[18px]" />
              </div>
            </div>

            <div className="mt-3 text-xs text-slate-400">
              {card.description}
            </div>
          </div>
        );
      })}
    </section>
  );
}