import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import type { DistributionReportPublic } from "@/client"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

const CHART_COLORS = [
  "#FF4B5F",
  "#3B82F6",
  "#10B981",
  "#F59E0B",
  "#8B5CF6",
  "#EC4899",
]

type DistributionReportPanelProps = {
  report: DistributionReportPublic
}

function countByKey<T>(
  items: T[],
  getKey: (item: T) => string,
): { name: string; count: number }[] {
  const map = new Map<string, number>()
  for (const item of items) {
    const key = getKey(item) || "—"
    map.set(key, (map.get(key) ?? 0) + 1)
  }
  return Array.from(map.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
}

export function DistributionReportPanel({ report }: DistributionReportPanelProps) {
  const byEmployee = countByKey(
    report.assignments,
    (a) => a.employee_full_name,
  )
  const byReason = countByKey(report.unplaced, (u) => u.reason)

  return (
    <div className="flex flex-col gap-6 rounded-lg border bg-card p-6">
      <div>
        <h2 className="text-lg font-semibold">Отчёт о распределении</h2>
        <p className="text-sm text-muted-foreground mt-1">{report.message}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-md border p-4">
          <p className="text-sm text-muted-foreground">Назначено</p>
          <p className="text-2xl font-bold">{report.assignments.length}</p>
        </div>
        <div className="rounded-md border p-4">
          <p className="text-sm text-muted-foreground">Не размещено</p>
          <p className="text-2xl font-bold">{report.unplaced.length}</p>
        </div>
      </div>

      {(byEmployee.length > 0 || byReason.length > 0) && (
        <div className="grid gap-6 lg:grid-cols-2">
          {byEmployee.length > 0 && (
            <div className="h-64">
              <p className="text-sm font-medium mb-2">Задачи по сотрудникам</p>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={byEmployee} margin={{ bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="name"
                    angle={-25}
                    textAnchor="end"
                    interval={0}
                    height={80}
                    tick={{ fontSize: 11 }}
                  />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#FF4B5F" name="Задач" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
          {byReason.length > 0 && (
            <div className="h-64">
              <p className="text-sm font-medium mb-2">
                Неразмещённые по причине
              </p>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={byReason}
                    dataKey="count"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label={(props) => {
                      const name = props.name ?? ""
                      const percent = props.percent ?? 0
                      return `${name} (${(percent * 100).toFixed(0)}%)`
                    }}
                  >
                    {byReason.map((entry, index) => (
                      <Cell
                        key={entry.name}
                        fill={CHART_COLORS[index % CHART_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {report.assignments.length > 0 && (
        <div>
          <h3 className="text-sm font-medium mb-2">Назначения</h3>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Сотрудник</TableHead>
                <TableHead>Точка</TableHead>
                <TableHead>Тип</TableHead>
                <TableHead>День</TableHead>
                <TableHead>Начало</TableHead>
                <TableHead>Окончание</TableHead>
                <TableHead>Причина</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {report.assignments.map((row, index) => (
                <TableRow key={`${row.employee_id}-${row.agent_point_id}-${index}`}>
                  <TableCell>{row.employee_full_name}</TableCell>
                  <TableCell>{row.agent_point_address ?? "—"}</TableCell>
                  <TableCell>{row.task_type_name}</TableCell>
                  <TableCell>{row.day_index}</TableCell>
                  <TableCell>{new Date(row.start_time).toLocaleString("ru-RU")}</TableCell>
                  <TableCell>{new Date(row.finish_time).toLocaleString("ru-RU")}</TableCell>
                  <TableCell>{row.reason}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {report.unplaced.length > 0 && (
        <div>
          <h3 className="text-sm font-medium mb-2">Не размещено</h3>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Точка</TableHead>
                <TableHead>Тип</TableHead>
                <TableHead>Причина</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {report.unplaced.map((row, index) => (
                <TableRow key={`${row.agent_point_id}-${index}`}>
                  <TableCell>{row.agent_point_address ?? "—"}</TableCell>
                  <TableCell>{row.task_type_name ?? "—"}</TableCell>
                  <TableCell>{row.reason}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  )
}
