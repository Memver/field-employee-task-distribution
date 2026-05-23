import type { ColumnDef } from "@tanstack/react-table"

import type { TaskPublic } from "@/client"
import {
  EmptyCell,
  formatAgentPoint,
  formatEmployee,
} from "@/lib/entityLabels"
import { formatDateTime } from "@/lib/formatDateTime"
import {
  formatApManagerVerdict,
  formatTaskStatusName,
  formatTaskTypeName,
} from "@/lib/i18n/ru"
import { ApmConfirmDialog } from "./ApmConfirmDialog"
import { UserActionsMenu } from "./UserActionsMenu"

export type TaskTableData = TaskPublic

const employeeColumn: ColumnDef<TaskTableData> = {
  id: "employee",
  header: "Сотрудник",
  cell: ({ row }) => formatEmployee(row.original.employee),
}

const taskTypeColumn: ColumnDef<TaskTableData> = {
  id: "task_type",
  header: "Тип задачи",
  cell: ({ row }) => formatTaskTypeName(row.original.task_type?.name),
}

const timeColumns: ColumnDef<TaskTableData>[] = [
  {
    accessorKey: "start_time",
    header: "Начало",
    cell: ({ row }) => formatDateTime(row.original.start_time),
  },
  {
    accessorKey: "finish_time",
    header: "Окончание",
    cell: ({ row }) => formatDateTime(row.original.finish_time),
  },
]

const agentPointColumn: ColumnDef<TaskTableData> = {
  id: "agent_point",
  header: "Агентская точка",
  cell: ({ row }) => formatAgentPoint(row.original.agent_point),
}

const statusColumn: ColumnDef<TaskTableData> = {
  id: "task_status",
  header: "Статус",
  cell: ({ row }) => formatTaskStatusName(row.original.task_status?.name),
}

export function getTaskColumns(isApm: boolean): ColumnDef<TaskTableData>[] {
  if (isApm) {
    return [
      agentPointColumn,
      taskTypeColumn,
      ...timeColumns,
      statusColumn,
      {
        id: "ap_verdict",
        header: "Вердикт",
        cell: ({ row }) => formatApManagerVerdict(row.original.ap_manager_confirmed),
      },
      {
        id: "actions",
        header: () => <span className="sr-only">Действия</span>,
        cell: ({ row }) => (
          <div className="flex justify-end">
            <ApmConfirmDialog task={row.original} />
          </div>
        ),
      },
    ]
  }

  return [
    taskTypeColumn,
    ...timeColumns,
    agentPointColumn,
    employeeColumn,
    statusColumn,
    {
      accessorKey: "comment",
      header: "Комментарий",
      cell: ({ row }) => <EmptyCell value={row.original.comment} />,
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
}

export const columns = getTaskColumns(false)
