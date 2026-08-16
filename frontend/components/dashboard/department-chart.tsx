"use client";

import { useEffect, useState } from "react";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { getDepartmentBreakdown } from "@/lib/api/dashboard";
import type { DepartmentBreakdownItem } from "@/lib/api/types";

const COLORS = ["#111827", "#2563eb", "#059669", "#d97706", "#dc2626", "#7c3aed"];

export function DepartmentChart() {
  const [data, setData] = useState<DepartmentBreakdownItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getDepartmentBreakdown()
      .then(setData)
      .catch((err) =>
        setError(
          err instanceof Error ? err.message : "Failed to load breakdown.",
        ),
      );
  }, []);

  return (
    <div className="rounded-xl border bg-white p-5">
      <h2 className="text-sm font-semibold">Department Breakdown</h2>
      <p className="mt-1 text-xs text-muted-foreground">
        Appointments by department
      </p>

      {error ? (
        <p className="mt-4 text-sm text-red-700">{error}</p>
      ) : (
        <div className="mt-4 flex items-center gap-6">
          <div className="h-56 w-56 shrink-0">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  dataKey="count"
                  nameKey="department"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={2}
                >
                  {data.map((entry, index) => (
                    <Cell
                      key={entry.department}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <ul className="space-y-2 text-sm">
            {data.map((item, index) => (
              <li key={item.department} className="flex items-center gap-2">
                <span
                  className="h-2.5 w-2.5 rounded-full"
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                />
                <span className="font-medium">{item.department}</span>
                <span className="text-muted-foreground">
                  {item.percentage}%
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
