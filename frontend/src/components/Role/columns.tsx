import type { ColumnDef } from "@tanstack/react-table"

import type { RolePublic } from "@/client"
import { formatRoleName } from "@/lib/i18n/ru"
import { cn } from "@/lib/utils"
import { UserActionsMenu } from "./UserActionsMenu"

export type RoleTableData = RolePublic

export const columns: ColumnDef<RoleTableData>[] = [
  {
    accessorKey: "name",
    header: "Название",
    cell: ({ row }) => {
      const value = formatRoleName(row.original.name)
      return (
        <span className={cn(value === "—" && "text-muted-foreground")}>
          {value}
        </span>
      )
    },
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Действия</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <UserActionsMenu role={row.original} />
      </div>
    ),
  },
]
