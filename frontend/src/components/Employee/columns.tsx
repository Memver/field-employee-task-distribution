import type { ColumnDef } from "@tanstack/react-table"

import type { EmployeePublic } from "@/client"
import { UserActionsMenu } from "./UserActionsMenu"

export type EmployeeTableData = EmployeePublic

export const columns: ColumnDef<EmployeeTableData>[] = [
  { accessorKey: "user_id", header: "ID пользователя" },
  { accessorKey: "grade_id", header: "ID грейда" },
  { accessorKey: "start_location_id", header: "ID стартовой локации" },
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
