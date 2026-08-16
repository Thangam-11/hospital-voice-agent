"use client";

import { Bell, Search } from "lucide-react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { getPatients } from "@/lib/api/patients";
import type { Patient } from "@/lib/api/types";

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export default function Header({
  title = "Overview",
  subtitle = "Hospital operations at a glance",
}: HeaderProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Patient[]>([]);
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Debounced live search against /patients?search=
  useEffect(() => {
    if (query.trim().length < 2) {
      setResults([]);
      setOpen(false);
      return;
    }

    const timeout = setTimeout(() => {
      getPatients(query)
        .then((patients) => {
          setResults(patients);
          setOpen(true);
        })
        .catch(() => setResults([]));
    }, 300);

    return () => clearTimeout(timeout);
  }, [query]);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const today = new Date().toLocaleDateString("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  });

  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-8 py-4">
      <div>
        <h1 className="text-[19px] font-semibold tracking-tight text-slate-900">
          {title}
        </h1>
        <p className="mt-0.5 text-[12.5px] text-slate-400">{subtitle}</p>
      </div>

      <div className="flex items-center gap-5">
        <div ref={containerRef} className="relative">
          <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3.5 py-2 text-sm text-slate-400 transition-colors focus-within:border-[#0D9488]/40 focus-within:bg-white focus-within:ring-2 focus-within:ring-[#0D9488]/10">
            <Search className="h-[15px] w-[15px]" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => results.length > 0 && setOpen(true)}
              placeholder="Search patients, appointments..."
              className="w-64 bg-transparent text-slate-700 outline-none placeholder:text-slate-400"
            />
            <kbd className="rounded border border-slate-200 bg-white px-1.5 py-0.5 text-[10px] font-medium text-slate-400">
              Ctrl K
            </kbd>
          </div>

          {open && results.length > 0 && (
            <div className="absolute right-0 z-10 mt-2 w-72 overflow-hidden rounded-lg border border-slate-200 bg-white shadow-lg shadow-slate-200/50">
              {results.map((patient) => (
                <Link
                  key={patient.id}
                  href={`/patients/${patient.id}`}
                  className="block px-4 py-2.5 text-sm transition-colors hover:bg-slate-50"
                  onClick={() => setOpen(false)}
                >
                  <p className="font-medium text-slate-900">
                    {patient.full_name}
                  </p>
                  <p className="text-xs text-slate-400">
                    {patient.phone_number}
                  </p>
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="h-8 w-px bg-slate-200" />

        <span className="text-[13px] font-medium text-slate-500">
          {today}
        </span>

        <button
          type="button"
          aria-label="Notifications"
          className="relative rounded-full p-2 text-slate-500 transition-colors hover:bg-slate-100"
        >
          <Bell className="h-[18px] w-[18px]" />
          <span className="absolute right-1 top-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-semibold text-white ring-2 ring-white">
            3
          </span>
        </button>

        <div className="h-8 w-px bg-slate-200" />

        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#0B1220] text-sm font-semibold text-white">
            T
          </div>
          <div className="text-sm leading-tight">
            <p className="font-medium text-slate-900">Thangarasu</p>
            <p className="text-[11.5px] text-slate-400">Administrator</p>
          </div>
        </div>
      </div>
    </header>
  );
}
