"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  LineChart,
  Line,
} from "recharts";

interface UIComponentData {
  component: string;
  data: any;
}

const CHART_COLORS = [
  "#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd", "#818cf8",
  "#4f46e5", "#7c3aed", "#5b21b6",
];

function ChartComponent({ data }: { data: any }) {
  const chartType = data.chart_type || "bar";
  const title = data.title || "Chart";
  const chartData = data.data || [];
  const xKey = data.x_key || Object.keys(chartData[0] || {})[0];
  const yKey = data.y_key || Object.keys(chartData[0] || {})[1];

  return (
    <div className="mt-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
      <h4 className="text-sm font-semibold text-slate-700 mb-3">{title}</h4>

      {chartType === "bar" && (
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey={xKey} tick={{ fontSize: 12, fill: "#64748b" }} />
            <YAxis tick={{ fontSize: 12, fill: "#64748b" }} />
            <Tooltip
              contentStyle={{
                borderRadius: "12px",
                border: "1px solid #e2e8f0",
                boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
              }}
            />
            <Bar dataKey={yKey} fill="#6366f1" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}

      {chartType === "line" && (
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey={xKey} tick={{ fontSize: 12, fill: "#64748b" }} />
            <YAxis tick={{ fontSize: 12, fill: "#64748b" }} />
            <Tooltip
              contentStyle={{
                borderRadius: "12px",
                border: "1px solid #e2e8f0",
              }}
            />
            <Line type="monotone" dataKey={yKey} stroke="#6366f1" strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      )}

      {chartType === "pie" && (
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie
              data={chartData}
              dataKey={data.value_key || yKey}
              nameKey={data.name_key || xKey}
              cx="50%"
              cy="50%"
              outerRadius={90}
              label={(props: any) => `${props.name || ''} ${((props.percent || 0) * 100).toFixed(0)}%`}
              labelLine={false}
            >
              {chartData.map((_: any, index: number) => (
                <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
              ))}
            </Pie>
            <Legend />
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

function TableComponent({ data }: { data: any }) {
  const title = data.summary || data.title || "Data Table";
  const rows = data.data || [];

  if (rows.length === 0) return null;

  const columns = Object.keys(rows[0]);

  return (
    <div className="mt-4 rounded-xl overflow-hidden border border-slate-200 bg-white">
      <div className="px-4 py-3 bg-slate-50 border-b border-slate-200">
        <h4 className="text-sm font-semibold text-slate-700">{title}</h4>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50/50">
              {columns.map((col) => (
                <th key={col} className="text-left px-4 py-2.5 text-xs font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-100">
                  {col.replace(/_/g, " ")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row: any, i: number) => (
              <tr key={i} className="hover:bg-slate-50 transition-colors border-b border-slate-50 last:border-0">
                {columns.map((col) => (
                  <td key={col} className="px-4 py-2.5 text-slate-700 font-medium">
                    {String(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatusCard({ data }: { data: any }) {
  return (
    <div className="mt-4 p-4 rounded-xl bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-100">
      <div className="grid grid-cols-2 gap-3">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
              {key.replace(/_/g, " ")}
            </span>
            <span className="text-sm font-bold text-slate-800 mt-0.5">{String(value)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function DynamicRenderer({ components }: { components: UIComponentData[] }) {
  if (!components || components.length === 0) return null;

  return (
    <div className="dynamic-components space-y-3">
      {components.map((comp, index) => {
        switch (comp.component) {
          case "chart":
            return <ChartComponent key={index} data={comp.data} />;
          case "table":
            return <TableComponent key={index} data={comp.data} />;
          case "status_card":
            return <StatusCard key={index} data={comp.data} />;
          default:
            return null;
        }
      })}
    </div>
  );
}
