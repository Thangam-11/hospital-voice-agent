"use client";

import { Search } from "lucide-react";
import { useEffect, useState } from "react";

import { getPatients } from "@/lib/api/patients";
import type { Patient } from "@/lib/api/types";

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[] | null>(null);
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const timeout = setTimeout(() => {
      getPatients(query || undefined)
        .then(setPatients)
        .catch((err) =>
          setError(err instanceof Error ? err.message : "Failed to load patients."),
        );
    }, 250);

    return () => clearTimeout(timeout);
  }, [query]);

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div className="relative w-80">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by name or phone..."
            className="w-full rounded-lg border border-slate-200 bg-white py-2.5 pl-9 pr-3 text-sm text-slate-700 outline-none transition-colors focus:border-[#0D9488]/40 focus:ring-2 focus:ring-[#0D9488]/10"
          />
        </div>

        {patients && (
          <span className="text-sm text-slate-400">
            {patients.length} patient{patients.length === 1 ? "" : "s"}
          </span>
        )}
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
        {error ? (
          <div className="p-6 text-sm text-red-700">{error}</div>
        ) : patients === null ? (
          <div className="p-10 text-center text-sm text-slate-400">
            Loading…
          </div>
        ) : patients.length === 0 ? (
          <div className="p-10 text-center text-sm text-slate-400">
            No patients found.
          </div>
        ) : (
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
                <th className="px-5 py-3 font-medium">Name</th>
                <th className="px-5 py-3 font-medium">Phone</th>
                <th className="px-5 py-3 font-medium">Date of Birth</th>
                <th className="px-5 py-3 font-medium">Gender</th>
                <th className="px-5 py-3 font-medium">Email</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {patients.map((patient) => (
                <tr key={patient.id} className="hover:bg-slate-50/60">
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#0D9488]/10 text-xs font-semibold text-[#0D9488]">
                        {patient.full_name.charAt(0)}
                      </div>
                      <span className="font-medium text-slate-900">
                        {patient.full_name}
                      </span>
                    </div>
                  </td>
                  <td className="px-5 py-3.5 text-slate-600">
                    {patient.phone_number}
                  </td>
                  <td className="px-5 py-3.5 text-slate-600">
                    {patient.date_of_birth}
                  </td>
                  <td className="px-5 py-3.5 text-slate-600">
                    {patient.gender ?? "—"}
                  </td>
                  <td className="px-5 py-3.5 text-slate-600">
                    {patient.email ?? "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
