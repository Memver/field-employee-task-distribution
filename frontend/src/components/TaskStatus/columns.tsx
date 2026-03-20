import type { ColumnDef } from "@tanstack/react-table"

import type { TaskStatusPublic } from "@/client"
import { cn } from "@/lib/utils"
import { UserActionsMenu } from "./UserActionsMenu"

export type TaskStatusTableData = TaskStatusPublic

export const columns: ColumnDef<TaskStatusTableData>[] = [
  {
    accessorKey: "name",
    header: "Название",
    cell: ({ row }) => {
      const value = row.original.name
      return (
        <span className={cn(!value && "text-muted-foreground")}>
          {value || "N/A"}
        </span>
      )
    },
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Действия</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <UserActionsMenu taskStatus={row.original} />
      </div>
    ),
  },
]
