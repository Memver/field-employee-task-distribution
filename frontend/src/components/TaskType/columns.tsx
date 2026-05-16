import type { ColumnDef } from "@tanstack/react-table"

import type { TaskTypePublic } from "@/client"
import { UserActionsMenu } from "./UserActionsMenu"

export type TaskTypeTableData = TaskTypePublic

export const columns: ColumnDef<TaskTypeTableData>[] = [
  { accessorKey: "name", header: "Название" },
  { accessorKey: "execution_time", header: "Время выполнения" },
  {
    id: "min_grade",
    header: "Мин. грейд",
    cell: ({ row }) => row.original.min_grade?.name ?? "—",
  },
  {
    id: "priority",
    header: "Приоритет",
    cell: ({ row }) => row.original.priority?.name ?? "—",
  },
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
