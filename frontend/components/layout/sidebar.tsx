"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  CalendarDays,
  Mic,
  PhoneCall,
  Stethoscope,
  Building2,
  BarChart3,
  Settings,
  Sparkles,
  ChevronDown,
} from "lucide-react";

const mainNavigation = [
  {
    name: "Overview",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Patients",
    href: "/patients",
    icon: Users,
  },
  {
    name: "Appointments",
    href: "/appointments",
    icon: CalendarDays,
  },
  {
    name: "Voice Agent",
    href: "/voice-agent",
    icon: Mic,
  },
  {
    name: "Call History",
    href: "/calls",
    icon: PhoneCall,
  },
];

const managementNavigation = [
  {
    name: "Doctors",
    href: "/doctors",
    icon: Stethoscope,
  },
  {
    name: "Departments",
    href: "/departments",
    icon: Building2,
  },
  {
    name: "Reports",
    href: "/reports",
    icon: BarChart3,
  },
];

export function Sidebar() {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === "/dashboard") {
      return pathname === "/dashboard";
    }

    return pathname.startsWith(href);
  };

  return (
    <aside className="fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r bg-white">
      {/* Brand */}
      <div className="flex h-16 items-center border-b px-5">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <Sparkles className="h-5 w-5" />
          </div>

          <div>
            <h1 className="text-sm font-semibold tracking-tight">
              MediVoice AI
            </h1>
            <p className="text-xs text-muted-foreground">
              Hospital Assistant
            </p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto px-3 py-5">
        <nav className="space-y-1">
          {mainNavigation.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);

            return (
              <Link
                key={item.name}
                href={item.href}
                className={`group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  active
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                <Icon
                  className={`h-[18px] w-[18px] ${
                    active
                      ? "text-primary"
                      : "text-muted-foreground group-hover:text-foreground"
                  }`}
                />

                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        <div className="my-5 border-t" />

        <p className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
          Management
        </p>

        <nav className="space-y-1">
          {managementNavigation.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);

            return (
              <Link
                key={item.name}
                href={item.href}
                className={`group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  active
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                <Icon className="h-[18px] w-[18px]" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        <div className="my-5 border-t" />

        <Link
          href="/settings"
          className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        >
          <Settings className="h-[18px] w-[18px]" />
          <span>Settings</span>
        </Link>
      </div>

      {/* Voice Agent CTA */}
      <div className="px-3 pb-4">
        <Link
          href="/voice-agent"
          className="group block rounded-xl border bg-gradient-to-br from-primary/5 to-primary/10 p-4 transition-colors hover:border-primary/30"
        >
          <div className="flex items-center justify-between">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-primary-foreground">
              <Mic className="h-4 w-4" />
            </div>

            <span className="text-primary opacity-0 transition-opacity group-hover:opacity-100">
              →
            </span>
          </div>

          <p className="mt-3 text-sm font-semibold">Start Voice Agent</p>

          <p className="mt-1 text-xs text-muted-foreground">
            Talk to AI Assistant
          </p>
        </Link>
      </div>

      {/* User */}
      <div className="border-t p-3">
        <button className="flex w-full items-center gap-3 rounded-lg p-2 text-left hover:bg-muted">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-muted text-sm font-semibold">
            T
          </div>

          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">Thangarasu</p>
            <p className="truncate text-xs text-muted-foreground">
              Administrator
            </p>
          </div>

          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        </button>
      </div>
    </aside>
  );
}