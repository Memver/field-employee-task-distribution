import type { ColumnDef } from "@tanstack/react-table"

import type { EmployeePublic } from "@/client"
import { formatLocation, formatUserRef } from "@/lib/entityLabels"
import { UserActionsMenu } from "./UserActionsMenu"

export type EmployeeTableData = EmployeePublic

export const columns: ColumnDef<EmployeeTableData>[] = [
  {
    id: "user",
    header: "Пользователь",
    cell: ({ row }) => formatUserRef(row.original.user),
  },
  {
    id: "grade",
    header: "Грейд",
    cell: ({ row }) => row.original.grade?.name ?? "—",
  },
  {
    id: "start_location",
    header: "Стартовая локация",
    cell: ({ row }) => formatLocation(row.original.start_location),
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Действия</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <UserActionsMenu employee={row.original} />
      </div>
    ),
  },
]
