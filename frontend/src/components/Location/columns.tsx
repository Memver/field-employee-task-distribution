import type { ColumnDef } from "@tanstack/react-table"

import type { LocationPublic } from "@/client"
import { cn } from "@/lib/utils"
import { UserActionsMenu } from "./UserActionsMenu"

export type LocationTableData = LocationPublic & {}

export const columns: ColumnDef<LocationTableData>[] = [
  {
    accessorKey: "address",
    header: "Адрес",
    cell: ({ row }) => {
      const fullName = row.original.address
      return (
        <div className="flex items-center gap-2">
          <span
            className={cn("font-medium", !fullName && "text-muted-foreground")}
          >
            {fullName || "—"}
          </span>
        </div>
      )
    },
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Действия</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <UserActionsMenu location={row.original} />
      </div>
    ),
  },
]
