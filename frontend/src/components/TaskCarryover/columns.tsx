import type { ColumnDef } from "@tanstack/react-table"
import type { TaskCarryoverPublic } from "@/features/taskCarryovers/types"
import { formatTaskTypeName } from "@/lib/i18n/ru"
import { UserActionsMenu } from "./UserActionsMenu"

export type TaskCarryoverTableData = TaskCarryoverPublic

function formatDate(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }
  return date.toLocaleDateString("ru-RU")
}

export const columns: ColumnDef<TaskCarryoverTableData>[] = [
  {
    accessorKey: "agent_point.location.address",
    header: "Адрес точки",
    cell: ({ row }) => row.original.agent_point.location.address,
  },
  {
    accessorKey: "task_type.name",
    header: "Тип задачи",
    cell: ({ row }) => formatTaskTypeName(row.original.task_type.name),
  },
  {
    accessorKey: "planned_for_date",
    header: "Дата переноса",
    cell: ({ row }) => formatDate(row.original.planned_for_date),
  },
  {
    accessorKey: "source_reason",
    header: "Причина",
    cell: ({ row }) => (
      <span
        className="block max-w-[420px] truncate"
        title={row.original.source_reason}
      >
        {row.original.source_reason}
      </span>
    ),
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Действия</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <UserActionsMenu taskCarryover={row.original} />
      </div>
    ),
  },
]
