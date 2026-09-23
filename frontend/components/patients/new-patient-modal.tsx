"use client";

import { X } from "lucide-react";
import { useState } from "react";

import { createPatient } from "@/lib/api/patients";
import type { Patient } from "@/lib/api/types";

interface NewPatientModalProps {
  onClose: () => void;
  onCreated: (patient: Patient) => void;
}

export function NewPatientModal({ onClose, onCreated }: NewPatientModalProps) {
  const [fullName, setFullName] = useState("");
  const [dob, setDob] = useState("");
  const [phone, setPhone] = useState("");
  const [gender, setGender] = useState("");
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      const patient = await createPatient({
        full_name: fullName,
        date_of_birth: dob,
        phone_number: phone,
        gender: gender || undefined,
        email: email || undefined,
      });
      onCreated(patient);
      onClose();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to register patient. Confirm your backend has a POST /patients endpoint.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">
            New Patient
          </h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="rounded-full p-1.5 text-slate-400 hover:bg-slate-100"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">
              Full name
            </label>
            <input
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#0D9488]/40 focus:ring-2 focus:ring-[#0D9488]/10"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">
                Date of birth
              </label>
              <input
                required
                type="date"
                value={dob}
                onChange={(e) => setDob(e.target.value)}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#0D9488]/40 focus:ring-2 focus:ring-[#0D9488]/10"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">
                Gender
              </label>
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#0D9488]/40 focus:ring-2 focus:ring-[#0D9488]/10"
              >
                <option value="">—</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">
              Phone number
            </label>
            <input
              required
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+1 555 000 0000"
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#0D9488]/40 focus:ring-2 focus:ring-[#0D9488]/10"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">
              Email (optional)
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#0D9488]/40 focus:ring-2 focus:ring-[#0D9488]/10"
            />
          </div>

          {error && <p className="text-xs text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-[#0D9488] py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#0F766E] disabled:opacity-60"
          >
            {submitting ? "Registering…" : "Register Patient"}
          </button>
        </form>
      </div>
    </div>
  );
}
