"use client";

import {
  CalendarDays,
  Mail,
  Phone,
  Plus,
  Search,
  UserRound,
} from "lucide-react";
import { useState } from "react";

const patients = [
  {
    id: "PAT-1001",
    name: "Ravi Kumar",
    age: 42,
    gender: "Male",
    phone: "+91 98765 43210",
    email: "ravi.kumar@example.com",
    department: "Cardiology",
    lastVisit: "Aug 14, 2026",
    status: "Active",
  },
  {
    id: "PAT-1002",
    name: "Priya Sharma",
    age: 35,
    gender: "Female",
    phone: "+91 98765 12345",
    email: "priya.sharma@example.com",
    department: "General Medicine",
    lastVisit: "Aug 14, 2026",
    status: "Active",
  },
  {
    id: "PAT-1003",
    name: "Arun Singh",
    age: 51,
    gender: "Male",
    phone: "+91 98765 67890",
    email: "arun.singh@example.com",
    department: "Neurology",
    lastVisit: "Aug 12, 2026",
    status: "Active",
  },
  {
    id: "PAT-1004",
    name: "Meena Devi",
    age: 28,
    gender: "Female",
    phone: "+91 98765 24680",
    email: "meena.devi@example.com",
    department: "Pediatrics",
    lastVisit: "Aug 10, 2026",
    status: "Active",
  },
  {
    id: "PAT-1005",
    name: "Suresh Kumar",
    age: 47,
    gender: "Male",
    phone: "+91 98765 13579",
    email: "suresh.kumar@example.com",
    department: "Orthopedics",
    lastVisit: "Aug 08, 2026",
    status: "Inactive",
  },
];

function StatusBadge({ status }: { status: string }) {
  if (status === "Active") {
    return (
      <span className="inline-flex rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
        Active
      </span>
    );
  }

  return (
    <span className="inline-flex rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground">
      Inactive
    </span>
  );
}

export default function PatientsPage() {
  const [search, setSearch] = useState("");
  const [showModal, setShowModal] = useState(false);

  const filteredPatients = patients.filter((patient) => {
    const query = search.toLowerCase();

    return (
      patient.name.toLowerCase().includes(query) ||
      patient.id.toLowerCase().includes(query) ||
      patient.phone.toLowerCase().includes(query) ||
      patient.department.toLowerCase().includes(query)
    );
  });

  return (
    <div className="mx-auto max-w-[1600px] px-6 py-8">
      {/* Header */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Patients
          </h1>

          <p className="mt-1 text-sm text-muted-foreground">
            Manage patient profiles and healthcare information.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground shadow-sm hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          Add Patient
        </button>
      </div>

      {/* Statistics */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border bg-white p-5">
          <p className="text-sm text-muted-foreground">
            Total Patients
          </p>

          <p className="mt-2 text-2xl font-semibold">
            1,248
          </p>

          <p className="mt-1 text-xs text-emerald-600">
            +12 this month
          </p>
        </div>

        <div className="rounded-xl border bg-white p-5">
          <p className="text-sm text-muted-foreground">
            Active Patients
          </p>

          <p className="mt-2 text-2xl font-semibold">
            1,102
          </p>

          <p className="mt-1 text-xs text-muted-foreground">
            88.3% of total
          </p>
        </div>

        <div className="rounded-xl border bg-white p-5">
          <p className="text-sm text-muted-foreground">
            New This Month
          </p>

          <p className="mt-2 text-2xl font-semibold">
            86
          </p>

          <p className="mt-1 text-xs text-emerald-600">
            +8.4% from last month
          </p>
        </div>

        <div className="rounded-xl border bg-white p-5">
          <p className="text-sm text-muted-foreground">
            Today&apos;s Visits
          </p>

          <p className="mt-2 text-2xl font-semibold">
            45
          </p>

          <p className="mt-1 text-xs text-muted-foreground">
            Across all departments
          </p>
        </div>
      </div>

      {/* Search */}
      <div className="mb-4 rounded-xl border bg-white p-4">
        <div className="relative max-w-xl">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by patient name, ID, phone, or department..."
            className="h-10 w-full rounded-lg border bg-white pl-9 pr-3 text-sm outline-none placeholder:text-muted-foreground focus:border-primary"
          />
        </div>
      </div>

      {/* Patient table */}
      <div className="overflow-hidden rounded-xl border bg-white">
        <div className="border-b px-5 py-4">
          <h2 className="text-sm font-semibold">
            Patient Directory
          </h2>

          <p className="mt-1 text-xs text-muted-foreground">
            {filteredPatients.length} patients shown
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[1000px] text-sm">
            <thead>
              <tr className="border-b bg-muted/20">
                <th className="px-5 py-3 text-left text-xs font-medium text-muted-foreground">
                  Patient
                </th>

                <th className="px-5 py-3 text-left text-xs font-medium text-muted-foreground">
                  Contact
                </th>

                <th className="px-5 py-3 text-left text-xs font-medium text-muted-foreground">
                  Age / Gender
                </th>

                <th className="px-5 py-3 text-left text-xs font-medium text-muted-foreground">
                  Department
                </th>

                <th className="px-5 py-3 text-left text-xs font-medium text-muted-foreground">
                  Last Visit
                </th>

                <th className="px-5 py-3 text-left text-xs font-medium text-muted-foreground">
                  Status
                </th>
              </tr>
            </thead>

            <tbody className="divide-y">
              {filteredPatients.map((patient) => (
                <tr
                  key={patient.id}
                  className="transition-colors hover:bg-muted/20"
                >
                  {/* Patient */}
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
                        {patient.name.charAt(0)}
                      </div>

                      <div>
                        <p className="font-medium">
                          {patient.name}
                        </p>

                        <p className="text-xs text-muted-foreground">
                          {patient.id}
                        </p>
                      </div>
                    </div>
                  </td>

                  {/* Contact */}
                  <td className="px-5 py-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-xs">
                        <Phone className="h-3.5 w-3.5 text-muted-foreground" />
                        {patient.phone}
                      </div>

                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Mail className="h-3.5 w-3.5" />
                        {patient.email}
                      </div>
                    </div>
                  </td>

                  {/* Age */}
                  <td className="px-5 py-4">
                    <p>{patient.age} years</p>

                    <p className="text-xs text-muted-foreground">
                      {patient.gender}
                    </p>
                  </td>

                  {/* Department */}
                  <td className="px-5 py-4 text-muted-foreground">
                    {patient.department}
                  </td>

                  {/* Last visit */}
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-2">
                      <CalendarDays className="h-4 w-4 text-muted-foreground" />

                      <span>{patient.lastVisit}</span>
                    </div>
                  </td>

                  {/* Status */}
                  <td className="px-5 py-4">
                    <StatusBadge status={patient.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Patient Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-xl rounded-2xl border bg-white shadow-xl">
            {/* Modal header */}
            <div className="border-b px-6 py-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <UserRound className="h-5 w-5" />
                </div>

                <div>
                  <h2 className="text-lg font-semibold">
                    Add Patient
                  </h2>

                  <p className="mt-1 text-sm text-muted-foreground">
                    Create a new patient profile.
                  </p>
                </div>
              </div>
            </div>

            {/* Form */}
            <div className="space-y-4 p-6">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1.5 block text-sm font-medium">
                    First Name
                  </label>

                  <input
                    placeholder="First name"
                    className="h-10 w-full rounded-lg border px-3 text-sm outline-none focus:border-primary"
                  />
                </div>

                <div>
                  <label className="mb-1.5 block text-sm font-medium">
                    Last Name
                  </label>

                  <input
                    placeholder="Last name"
                    className="h-10 w-full rounded-lg border px-3 text-sm outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1.5 block text-sm font-medium">
                    Phone
                  </label>

                  <input
                    type="tel"
                    placeholder="+91 XXXXX XXXXX"
                    className="h-10 w-full rounded-lg border px-3 text-sm outline-none focus:border-primary"
                  />
                </div>

                <div>
                  <label className="mb-1.5 block text-sm font-medium">
                    Email
                  </label>

                  <input
                    type="email"
                    placeholder="patient@example.com"
                    className="h-10 w-full rounded-lg border px-3 text-sm outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1.5 block text-sm font-medium">
                    Date of Birth
                  </label>

                  <input
                    type="date"
                    className="h-10 w-full rounded-lg border px-3 text-sm outline-none focus:border-primary"
                  />
                </div>

                <div>
                  <label className="mb-1.5 block text-sm font-medium">
                    Gender
                  </label>

                  <select className="h-10 w-full rounded-lg border bg-white px-3 text-sm">
                    <option>Select gender</option>
                    <option>Male</option>
                    <option>Female</option>
                    <option>Other</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium">
                  Address
                </label>

                <textarea
                  rows={3}
                  placeholder="Patient address"
                  className="w-full resize-none rounded-lg border px-3 py-2 text-sm outline-none focus:border-primary"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 border-t px-6 py-4">
              <button
                type="button"
                onClick={() => setShowModal(false)}
                className="rounded-lg border px-4 py-2 text-sm font-medium hover:bg-muted"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={() => setShowModal(false)}
                className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
              >
                Create Patient
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}