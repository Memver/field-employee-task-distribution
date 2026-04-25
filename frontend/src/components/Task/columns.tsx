import type { ColumnDef } from "@tanstack/react-table"

import type { TaskPublic } from "@/client"
import { TaskActionsMenu } from "./TaskActionsMenu"

export type TaskTableData = TaskPublic

export const columns: ColumnDef<TaskTableData>[] = [
  { accessorKey: "start_time", header: "Начало" },
  { accessorKey: "finish_time", header: "Окончание" },
  { accessorKey: "comment", header: "Комментарий" },
  { accessorKey: "employee_id", header: "ID сотрудника" },
  { accessorKey: "task_type_id", header: "ID типа задачи" },
  { accessorKey: "agent_point_id", header: "ID точки" },
  { accessorKey: "task_status_id", header: "ID статуса" },
  {
    id: "actions",
    header: () => <span className="sr-only">Действия</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <TaskActionsMenu task={row.original} />
      </div>
    ),
  },
]
