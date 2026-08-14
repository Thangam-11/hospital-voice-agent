"use client";

import {
  Bell,
  CalendarDays,
  Search,
  Menu,
} from "lucide-react";

export function Header() {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center border-b bg-white/95 px-6 backdrop-blur">
      {/* Mobile menu */}
      <button
        className="mr-4 rounded-lg p-2 text-muted-foreground hover:bg-muted lg:hidden"
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      {/* Page title */}
      <div className="flex-1">
        <h2 className="text-base font-semibold tracking-tight">
          Overview
        </h2>
      </div>

      {/* Search */}
      <button className="mr-3 hidden h-9 w-72 items-center gap-2 rounded-lg border bg-muted/30 px-3 text-sm text-muted-foreground transition-colors hover:bg-muted sm:flex">
        <Search className="h-4 w-4" />

        <span className="flex-1 text-left">
          Search patients, appointments...
        </span>

        <kbd className="rounded border bg-white px-1.5 py-0.5 text-[10px]">
          Ctrl K
        </kbd>
      </button>

      {/* Date */}
      <div className="mr-4 hidden items-center gap-2 text-sm md:flex">
        <CalendarDays className="h-4 w-4 text-muted-foreground" />

        <span className="text-muted-foreground">
          Aug 14, 2026
        </span>
      </div>

      {/* Notifications */}
      <button
        className="relative rounded-lg p-2 text-muted-foreground hover:bg-muted"
        aria-label="Notifications"
      >
        <Bell className="h-5 w-5" />

        <span className="absolute right-1 top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[9px] font-medium text-white">
          3
        </span>
      </button>

      {/* User */}
      <div className="ml-3 flex items-center gap-2 border-l pl-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
          T
        </div>

        <div className="hidden text-left sm:block">
          <p className="text-sm font-medium">Thangarasu</p>
          <p className="text-xs text-muted-foreground">
            Administrator
          </p>
        </div>
      </div>
    </header>
  );
}