"use client";

import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

const departmentData = [
  {
    name: "Cardiology",
    value: 30,
  },
  {
    name: "General Medicine",
    value: 25,
  },
  {
    name: "Orthopedics",
    value: 20,
  },
  {
    name: "Pediatrics",
    value: 15,
  },
  {
    name: "Neurology",
    value: 10,
  },
];

const chartColors = [
  "#2563eb",
  "#14b8a6",
  "#8b5cf6",
  "#f59e0b",
  "#64748b",
];

export function DepartmentChart() {
  return (
    <div className="rounded-xl border bg-white p-5">
      {/* Header */}
      <div className="mb-5">
        <h2 className="text-sm font-semibold">
          Appointments by Department
        </h2>

        <p className="mt-1 text-xs text-muted-foreground">
          Distribution of appointments by department
        </p>
      </div>

      <div className="grid items-center gap-6 md:grid-cols-2">
        {/* Chart */}
        <div className="h-[260px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={departmentData}
                cx="50%"
                cy="50%"
                innerRadius={65}
                outerRadius={95}
                paddingAngle={2}
                dataKey="value"
                stroke="white"
                strokeWidth={2}
              >
                {departmentData.map((entry, index) => (
                  <Cell
                    key={entry.name}
                    fill={chartColors[index]}
                  />
                ))}
              </Pie>

              <Tooltip
                formatter={(value) => [
                  `${value}%`,
                  "Appointments",
                ]}
                contentStyle={{
                  borderRadius: "10px",
                  border: "1px solid #e5e7eb",
                  backgroundColor: "#ffffff",
                  fontSize: "12px",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Legend */}
        <div className="space-y-4">
          {departmentData.map((department, index) => (
            <div
              key={department.name}
              className="flex items-center justify-between"
            >
              <div className="flex items-center gap-2.5">
                <span
                  className="h-2.5 w-2.5 rounded-full"
                  style={{
                    backgroundColor: chartColors[index],
                  }}
                />

                <span className="text-sm text-muted-foreground">
                  {department.name}
                </span>
              </div>

              <span className="text-sm font-medium">
                {department.value}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}