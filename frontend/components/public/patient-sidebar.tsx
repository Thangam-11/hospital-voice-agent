"use client";

import { CalendarPlus, CalendarSearch, Info, Mic } from "lucide-react";

const NAV_ITEMS = [
  { key: "talk", label: "Talk to AI", icon: Mic },
  { key: "book", label: "Book Appointment", icon: CalendarPlus },
  { key: "check", label: "Check Appointment", icon: CalendarSearch },
  { key: "info", label: "Hospital Info", icon: Info },
] as const;

export type PatientNavKey = (typeof NAV_ITEMS)[number]["key"];

export function PatientSidebar({
  active,
  onSelect,
}: {
  active: PatientNavKey | null;
  onSelect: (key: PatientNavKey) => void;
}) {
  return (
    <aside className="flex h-screen w-64 shrink-0 flex-col bg-[#0B1220] text-slate-300">
      <div className="flex items-center gap-3 px-5 pb-5 pt-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#0D9488]">
          <Mic className="h-4 w-4 text-white" />
        </div>
        <div>
          <p className="text-sm font-semibold leading-none text-white">
            MediVoice AI
          </p>
          <p className="mt-1 text-[11px] tracking-wide text-slate-500">
            HOSPITAL ASSISTANT
          </p>
        </div>
      </div>

      <div className="mx-5 h-px bg-white/5" />

      <nav className="flex-1 space-y-0.5 px-3 py-5">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = active === item.key;

          return (
            <button
              key={item.key}
              type="button"
              onClick={() => onSelect(item.key)}
              className={`group relative flex w-full items-center gap-3 rounded-md py-2.5 pl-4 pr-3 text-left text-[13.5px] font-medium transition-colors ${
                isActive
                  ? "bg-white/[0.06] text-white"
                  : "text-slate-400 hover:bg-white/[0.04] hover:text-slate-200"
              }`}
            >
              <span
                className={`absolute left-0 top-1/2 h-4 w-[3px] -translate-y-1/2 rounded-r-full transition-opacity ${
                  isActive ? "bg-[#2DD4BF] opacity-100" : "opacity-0"
                }`}
              />
              <Icon
                className={`h-[17px] w-[17px] ${
                  isActive
                    ? "text-[#2DD4BF]"
                    : "text-slate-500 group-hover:text-slate-300"
                }`}
              />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div className="mx-5 h-px bg-white/5" />

      <div className="px-5 py-4">
        <a
          href="/login"
          className="text-[12px] font-medium text-slate-500 hover:text-slate-300"
        >
          Staff sign in →
        </a>
      </div>
    </aside>
  );
}
