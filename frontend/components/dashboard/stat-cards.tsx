import {
  CalendarDays,
  Clock3,
  PhoneCall,
  Users,
} from "lucide-react";

const stats = [
  {
    title: "Total Patients",
    value: "1,248",
    change: "+12.5%",
    description: "from yesterday",
    icon: Users,
  },
  {
    title: "Appointments Today",
    value: "45",
    change: "+8.2%",
    description: "from yesterday",
    icon: CalendarDays,
  },
  {
    title: "Upcoming Appointments",
    value: "18",
    change: null,
    description: "Next 24 hours",
    icon: Clock3,
  },
  {
    title: "AI Calls Today",
    value: "32",
    change: "+20.3%",
    description: "from yesterday",
    icon: PhoneCall,
  },
];

export function StatCards() {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {stats.map((stat) => {
        const Icon = stat.icon;

        return (
          <div
            key={stat.title}
            className="rounded-xl border bg-white p-5 transition-shadow hover:shadow-sm"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </p>

                <p className="mt-2 text-2xl font-semibold tracking-tight">
                  {stat.value}
                </p>
              </div>

              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Icon className="h-5 w-5" />
              </div>
            </div>

            <div className="mt-3 flex items-center gap-1 text-xs">
              {stat.change && (
                <span className="font-medium text-emerald-600">
                  ↑ {stat.change}
                </span>
              )}

              <span className="text-muted-foreground">
                {stat.description}
              </span>
            </div>
          </div>
        );
      })}
    </section>
  );
}