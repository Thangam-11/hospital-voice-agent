"use client";

import {
  CalendarDays,
  LayoutGrid,
  LogOut,
  Mic,
  PhoneCall,
  Settings,
  Users,
} from "lucide-react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { getCurrentUser, logout } from "@/lib/api/auth";
import type { AuthUser } from "@/lib/api/auth";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: LayoutGrid },
  { href: "/dashboard/patients", label: "Patients", icon: Users },
  { href: "/dashboard/appointments", label: "Appointments", icon: CalendarDays },
  { href: "/dashboard/voice-agents", label: "Voice Agent", icon: Mic },
  { href: "/dashboard/call-history", label: "Call History", icon: PhoneCall },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch(() => setUser(null));
  }, []);

  async function handleLogout() {
    await logout();
    router.push("/login");
  }

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
          const active =
            item.href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname?.startsWith(item.href);

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

      <div className="mx-5 h-px bg-white/5" />

      <div className="space-y-2 px-3 py-4">
        <div className="flex items-center gap-3 px-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 text-sm font-semibold text-white">
            {user?.full_name?.charAt(0)?.toUpperCase() ?? "?"}
          </div>
          <div className="min-w-0">
            <p className="truncate text-[13px] font-medium text-white">
              {user?.full_name ?? "Loading…"}
            </p>
            <p className="text-[11px] capitalize text-slate-500">
              {user?.role?.toLowerCase() ?? ""}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-md px-2 py-2 text-[13px] font-medium text-slate-400 transition-colors hover:bg-white/[0.04] hover:text-slate-200"
        >
          <LogOut className="h-4 w-4" />
          Log out
        </button>
      </div>
    </aside>
  );
}
