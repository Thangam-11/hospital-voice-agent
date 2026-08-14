"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const appointmentData = [
  { day: "Mon", appointments: 42 },
  { day: "Tue", appointments: 55 },
  { day: "Wed", appointments: 48 },
  { day: "Thu", appointments: 64 },
  { day: "Fri", appointments: 58 },
  { day: "Sat", appointments: 36 },
  { day: "Sun", appointments: 28 },
];

export function AppointmentTrendChart() {
  return (
    <div className="rounded-xl border bg-white p-5">
      {/* Header */}
      <div className="mb-5 flex items-start justify-between">
        <div>
          <h2 className="text-sm font-semibold">
            Appointment Trend
          </h2>

          <p className="mt-1 text-xs text-muted-foreground">
            Appointments over the last 7 days
          </p>
        </div>

        <button
          type="button"
          className="rounded-lg border px-3 py-1.5 text-xs font-medium text-muted-foreground hover:bg-muted"
        >
          Last 7 days
        </button>
      </div>

      {/* Chart */}
      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={appointmentData}
            margin={{
              top: 10,
              right: 20,
              left: 0,
              bottom: 10,
            }}
          >
            <CartesianGrid
              stroke="#e5e7eb"
              strokeDasharray="3 3"
              vertical={false}
            />

            <XAxis
              dataKey="day"
              axisLine={false}
              tickLine={false}
              tick={{
                fill: "#6b7280",
                fontSize: 12,
              }}
            />

            <YAxis
              axisLine={false}
              tickLine={false}
              allowDecimals={false}
              tick={{
                fill: "#6b7280",
                fontSize: 12,
              }}
            />

            <Tooltip
              cursor={{
                stroke: "#d1d5db",
              }}
              contentStyle={{
                borderRadius: "10px",
                border: "1px solid #e5e7eb",
                backgroundColor: "#ffffff",
                fontSize: "12px",
              }}
              formatter={(value) => [
                `${value} appointments`,
                "Appointments",
              ]}
            />

            <Line
              type="monotone"
              dataKey="appointments"
              stroke="#2563eb"
              strokeWidth={2.5}
              dot={{
                r: 4,
                fill: "#ffffff",
                stroke: "#2563eb",
                strokeWidth: 2,
              }}
              activeDot={{
                r: 6,
                fill: "#2563eb",
              }}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}