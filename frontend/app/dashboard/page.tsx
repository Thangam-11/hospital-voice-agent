import { AppointmentTrendChart } from "@/components/dashboard/appointment-trend-chart";
import { AppointmentsCard } from "@/components/dashboard/appointments-card";
import { DepartmentChart } from "@/components/dashboard/department-chart";
import { RecentAgentConversation } from "@/components/dashboard/recent-agent-conversation";
import { StatCards } from "@/components/dashboard/stat-cards";


export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-[1600px] px-6 py-8">
      {/* Page heading */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Good morning, Thangarasu 👋
          </h1>

          <p className="mt-1 text-sm text-muted-foreground">
            Here&apos;s what&apos;s happening at your hospital today.
          </p>
        </div>

        <div className="hidden text-right sm:block">
          <p className="text-sm font-medium">
            Thursday, Aug 14, 2026
          </p>

          <p className="mt-1 text-xs text-muted-foreground">
            10:30 AM
          </p>
        </div>
      </div>

      {/* Step 1 - Stat Cards */}
      <StatCards />

      {/* Step 2 + Step 3 - Charts */}
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <AppointmentTrendChart />
        <DepartmentChart />
      </div>

      {/* Step 4 - Recent Appointments */}
      <div className="mt-6">
        <AppointmentsCard />
      </div>
      {/* Step 5 - Recent AI Conversations */}
      <div className="mt-6">
      <RecentAgentConversation />
      </div>

    </div>
  );
}