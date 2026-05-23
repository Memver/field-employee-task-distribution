import { useMemo } from "react"

import type { TaskPublic } from "@/client"
import { formatAgentPoint, formatEmployee } from "@/lib/entityLabels"
import { formatTaskTypeName } from "@/lib/i18n/ru"

const WORKDAY_START_HOUR = 8
const WORKDAY_END_HOUR = 16
const WORKDAY_MS = (WORKDAY_END_HOUR - WORKDAY_START_HOUR) * 60 * 60 * 1000

type TimelineTask = {
  start: Date
  finish: Date
  label: string
}

type EmployeeDay = {
  employeeName: string
  dayKey: string
  travelEnd: Date | null
  tasks: TimelineTask[]
}

function dayKeyFromDate(date: Date): string {
  return date.toISOString().slice(0, 10)
}

function workdayStart(date: Date): Date {
  const start = new Date(date)
  start.setHours(WORKDAY_START_HOUR, 0, 0, 0)
  return start
}

function percentInWorkday(start: Date, moment: Date): number {
  const dayStart = workdayStart(start)
  const offset = moment.getTime() - dayStart.getTime()
  return Math.max(0, Math.min(100, (offset / WORKDAY_MS) * 100))
}

function buildEmployeeDays(tasks: TaskPublic[]): EmployeeDay[] {
  const byEmployeeDay = new Map<string, EmployeeDay>()

  for (const task of tasks) {
    if (!task.start_time || !task.finish_time || !task.employee) {
      continue
    }
    const start = new Date(task.start_time)
    const finish = new Date(task.finish_time)
    const employeeName = formatEmployee(task.employee)
    const key = `${task.employee_id}-${dayKeyFromDate(start)}`

    if (!byEmployeeDay.has(key)) {
      byEmployeeDay.set(key, {
        employeeName,
        dayKey: dayKeyFromDate(start),
        travelEnd: null,
        tasks: [],
      })
    }

    const group = byEmployeeDay.get(key)!
    group.tasks.push({
      start,
      finish,
      label: `${formatTaskTypeName(task.task_type?.name)} — ${formatAgentPoint(task.agent_point)}`,
    })
  }

  for (const group of byEmployeeDay.values()) {
    group.tasks.sort((a, b) => a.start.getTime() - b.start.getTime())
    if (group.tasks.length > 0) {
      group.travelEnd = group.tasks[0].start
    }
  }

  return Array.from(byEmployeeDay.values()).sort((a, b) =>
    a.employeeName.localeCompare(b.employeeName, "ru"),
  )
}

interface EmployeeDayTimelineProps {
  tasks: TaskPublic[]
}

export function EmployeeDayTimeline({ tasks }: EmployeeDayTimelineProps) {
  const employeeDays = useMemo(() => buildEmployeeDays(tasks), [tasks])

  if (employeeDays.length === 0) {
    return null
  }

  return (
    <div className="flex flex-col gap-4 rounded-lg border bg-card p-6">
      <div>
        <h2 className="text-lg font-semibold">Расписание на день</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Рабочий день с 08:00 до 16:00. Серый участок — дорога до первой задачи.
        </p>
      </div>
      {employeeDays.map((day) => {
        const anchor = new Date(`${day.dayKey}T08:00:00`)
        const travelStart = workdayStart(anchor)
        const travelEnd = day.travelEnd ?? travelStart

        return (
          <div key={`${day.employeeName}-${day.dayKey}`} className="space-y-2">
            <p className="text-sm font-medium">
              {day.employeeName}{" "}
              <span className="text-muted-foreground font-normal">
                ({new Date(day.dayKey).toLocaleDateString("ru-RU")})
              </span>
            </p>
            <div className="relative h-10 rounded-md bg-muted">
              <div className="absolute inset-y-0 left-0 right-0 flex items-center px-1 text-[10px] text-muted-foreground">
                <span>08:00</span>
                <span className="ml-auto">16:00</span>
              </div>
              {day.travelEnd && travelEnd > travelStart && (
                <div
                  className="absolute top-2 bottom-2 rounded bg-slate-400/70"
                  style={{
                    left: `${percentInWorkday(anchor, travelStart)}%`,
                    width: `${Math.max(percentInWorkday(anchor, travelEnd) - percentInWorkday(anchor, travelStart), 0.5)}%`,
                  }}
                  title={`Дорога: ${travelStart.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" })} – ${travelEnd.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" })}`}
                />
              )}
              {day.tasks.map((task, index) => (
                <div
                  key={`${task.label}-${index}`}
                  className="absolute top-2 bottom-2 rounded bg-[#FF4B5F]/85"
                  style={{
                    left: `${percentInWorkday(anchor, task.start)}%`,
                    width: `${Math.max(percentInWorkday(anchor, task.finish) - percentInWorkday(anchor, task.start), 0.5)}%`,
                  }}
                  title={`${task.label}: ${task.start.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" })} – ${task.finish.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" })}`}
                />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}
