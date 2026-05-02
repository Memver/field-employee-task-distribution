import type { ColumnDef } from "@tanstack/react-table"

import type { TaskTypePublic } from "@/client"
import { UserActionsMenu } from "./UserActionsMenu"

export type TaskTypeTableData = TaskTypePublic

export const columns: ColumnDef<TaskTypeTableData>[] = [
  { accessorKey: "name", header: "Название" },
  { accessorKey: "execution_time", header: "Время выполнения" },
  { accessorKey: "min_grade_id", header: "ID мин. грейда" },
  { accessorKey: "priority_id", header: "ID приоритета" },
  {
    id: "actions",
    header: () => <span className="sr-only">Действия</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <UserActionsMenu taskType={row.original} />
      </div>
    ),
  },
]
