"use client";

import { AppointmentTrendChart } from "@/components/dashboard/appointment-trend-chart";
import { AppointmentsCard } from "@/components/dashboard/appointments-card";
import { DepartmentChart } from "@/components/dashboard/department-chart";
import { RecentAgentConversation } from "@/components/dashboard/recent-agent-conversation";
import { StatCards } from "@/components/dashboard/stat-cards";

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <StatCards />

      <section>
        <div className="grid gap-5 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <AppointmentsCard />
          </div>
          <RecentAgentConversation />
        </div>
      </section>

      <section>
        <div className="mb-3 flex items-center gap-2">
          <h2 className="text-[13px] font-semibold uppercase tracking-wide text-slate-400">
            Analytics
          </h2>
          <div className="h-px flex-1 bg-slate-200" />
        </div>

        <div className="grid gap-5 lg:grid-cols-2">
          <AppointmentTrendChart />
          <DepartmentChart />
        </div>
      </section>
    </div>
  );
}