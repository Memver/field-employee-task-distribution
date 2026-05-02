import type { ColumnDef } from "@tanstack/react-table"

import type { PriorityPublic } from "@/client"
import { cn } from "@/lib/utils"
import { UserActionsMenu } from "./UserActionsMenu"

export type PriorityTableData = PriorityPublic

export const columns: ColumnDef<PriorityTableData>[] = [
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
    accessorKey: "level",
    header: "Уровень",
    cell: ({ row }) => (
      <span className="text-muted-foreground">{row.original.level}</span>
    ),
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Действия</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <UserActionsMenu priority={row.original} />
      </div>
    ),
  },
]
