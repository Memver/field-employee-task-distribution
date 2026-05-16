import type { ColumnDef } from "@tanstack/react-table"

import type { TaskPublic } from "@/client"
import {
  EmptyCell,
  formatAgentPoint,
  formatEmployee,
} from "@/lib/entityLabels"
import { UserActionsMenu } from "./UserActionsMenu"

export type TaskTableData = TaskPublic

export const columns: ColumnDef<TaskTableData>[] = [
  { accessorKey: "start_time", header: "Начало" },
  { accessorKey: "finish_time", header: "Окончание" },
  {
    accessorKey: "comment",
    header: "Комментарий",
    cell: ({ row }) => (
      <EmptyCell value={row.original.comment} />
    ),
  },
  {
    id: "employee",
    header: "Сотрудник",
    cell: ({ row }) => formatEmployee(row.original.employee),
  },
  {
    id: "task_type",
    header: "Тип задачи",
    cell: ({ row }) => row.original.task_type?.name ?? "—",
  },
  {
    id: "agent_point",
    header: "Агентская точка",
    cell: ({ row }) => formatAgentPoint(row.original.agent_point),
  },
  {
    id: "task_status",
    header: "Статус",
    cell: ({ row }) => row.original.task_status?.name ?? "—",
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Действия</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <UserActionsMenu task={row.original} />
      </div>
    ),
  },
]
