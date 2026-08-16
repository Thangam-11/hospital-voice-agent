"use client";

import {
  CalendarDays,
  LayoutGrid,
  Mic,
  PhoneCall,
  Users,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: LayoutGrid },
  { href: "/patients", label: "Patients", icon: Users },
  { href: "/appointments", label: "Appointments", icon: CalendarDays },
  { href: "/voice-agent", label: "Voice Agent", icon: Mic },
  { href: "/call-history", label: "Call History", icon: PhoneCall },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-64 shrink-0 flex-col bg-[#0B1220] text-slate-300">
      {/* Brand */}
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

      {/* Nav */}
      <nav className="flex-1 space-y-0.5 px-3 py-5">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const active = pathname?.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`group relative flex items-center gap-3 rounded-md py-2.5 pl-4 pr-3 text-[13.5px] font-medium transition-colors ${
                active
                  ? "bg-white/[0.06] text-white"
                  : "text-slate-400 hover:bg-white/[0.04] hover:text-slate-200"
              }`}
            >
              <span
                className={`absolute left-0 top-1/2 h-4 w-[3px] -translate-y-1/2 rounded-r-full transition-opacity ${
                  active ? "bg-[#2DD4BF] opacity-100" : "opacity-0"
                }`}
              />
              <Icon
                className={`h-[17px] w-[17px] ${
                  active ? "text-[#2DD4BF]" : "text-slate-500 group-hover:text-slate-300"
                }`}
              />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Voice agent CTA */}
      <div className="px-3 pb-3">
        <Link
          href="/voice-agent"
          className="flex items-center gap-3 rounded-lg border border-white/[0.06] bg-gradient-to-br from-[#0D9488]/20 to-[#0D9488]/5 px-3.5 py-3 transition-colors hover:from-[#0D9488]/25"
        >
          <span className="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#0D9488]">
            <Mic className="h-4 w-4 text-white" />
            <span className="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full border-2 border-[#0B1220] bg-[#2DD4BF]" />
          </span>
          <span>
            <span className="block text-[13px] font-semibold text-white">
              Start Voice Agent
            </span>
            <span className="block text-[11px] text-slate-400">
              Talk to AI Assistant
            </span>
          </span>
        </Link>
      </div>

      <div className="mx-5 h-px bg-white/5" />

      {/* User */}
      <div className="flex items-center gap-3 px-5 py-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 text-sm font-semibold text-white">
          T
        </div>
        <div className="min-w-0">
          <p className="truncate text-[13px] font-medium text-white">
            Thangarasu
          </p>
          <p className="text-[11px] text-slate-500">Administrator</p>
        </div>
      </div>
    </aside>
  );
}