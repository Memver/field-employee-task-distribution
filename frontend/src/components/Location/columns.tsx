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
            {fullName || "N/A"}
          </span>
        </div>
      )
    },
  },
  {
    accessorKey: "lat",
    header: "Широта",
    cell: ({ row }) => {
      const fullName = row.original.lat
      return (
        <span className={cn("font-medium", fullName == null && "text-muted-foreground")}>
          {fullName == null ? "N/A" : fullName}
        </span>
      )
    },
  },
  {
    accessorKey: "lon",
    header: "Долгота",
    cell: ({ row }) => {
      const fullName = row.original.lon
      return (
        <span className={cn("font-medium", fullName == null && "text-muted-foreground")}>
          {fullName == null ? "N/A" : fullName}
        </span>
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
