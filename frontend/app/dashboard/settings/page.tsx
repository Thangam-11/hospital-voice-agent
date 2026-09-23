"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { getCurrentUser, logout } from "@/lib/api/auth";
import type { AuthUser } from "@/lib/api/auth";

export default function SettingsPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loggingOut, setLoggingOut] = useState(false);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch(() => setUser(null));
  }, []);

  async function handleLogout() {
    setLoggingOut(true);
    await logout();
    router.push("/login");
  }

  return (
    <div className="max-w-xl space-y-5">
      <div className="rounded-xl border border-slate-200 bg-white p-6">
        <h2 className="text-sm font-semibold text-slate-900">Account</h2>
        <div className="mt-4 space-y-3 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Name</span>
            <span className="font-medium text-slate-900">
              {user?.full_name ?? "—"}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Email</span>
            <span className="font-medium text-slate-900">
              {user?.email ?? "—"}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Role</span>
            <span className="font-medium capitalize text-slate-900">
              {user?.role?.toLowerCase() ?? "—"}
            </span>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6">
        <h2 className="text-sm font-semibold text-slate-900">Session</h2>
        <p className="mt-1.5 text-sm text-slate-500">
          Sign out of MediVoice AI on this device.
        </p>
        <button
          type="button"
          onClick={handleLogout}
          disabled={loggingOut}
          className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm font-semibold text-red-600 transition-colors hover:bg-red-100 disabled:opacity-60"
        >
          {loggingOut ? "Signing out…" : "Log out"}
        </button>
      </div>
    </div>
  );
}
