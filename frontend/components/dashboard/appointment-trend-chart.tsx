"use client";

import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getAppointmentTrend } from "@/lib/api/dashboard";
import type { AppointmentTrendPoint } from "@/lib/api/types";

export function AppointmentTrendChart() {
  const [data, setData] = useState<AppointmentTrendPoint[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getAppointmentTrend(7)
      .then(setData)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Failed to load trend."),
      );
  }, []);

  return (
    <div className="rounded-xl border bg-white p-5">
      <h2 className="text-sm font-semibold">Appointment Trend</h2>
      <p className="mt-1 text-xs text-muted-foreground">Last 7 days</p>

      {error ? (
        <p className="mt-4 text-sm text-red-700">{error}</p>
      ) : (
        <div className="mt-4 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                tickFormatter={(d) =>
                  new Date(d).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                  })
                }
              />
              <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#111827"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
