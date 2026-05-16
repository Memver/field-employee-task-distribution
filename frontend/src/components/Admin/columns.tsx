import type { ColumnDef } from "@tanstack/react-table"

import type { UserPublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import { formatRoleName } from "@/lib/i18n/ru"
import { cn } from "@/lib/utils"
import { UserActionsMenu } from "./UserActionsMenu"

export type UserTableData = UserPublic & {
  isCurrentUser: boolean
}

export const columns: ColumnDef<UserTableData>[] = [
  {
    accessorKey: "name",
    header: "Имя",
    cell: ({ row }) => {
      const fullName = row.original.name
      return (
        <div className="flex items-center gap-2">
          <span
            className={cn("font-medium", !fullName && "text-muted-foreground")}
          >
            {fullName || "N/A"}
          </span>
          {row.original.isCurrentUser && (
            <Badge variant="outline" className="text-xs">
              Вы
            </Badge>
          )}
        </div>
      )
    },
  },
  {
    accessorKey: "surname",
    header: "Фамилия",
    cell: ({ row }) => {
      const fullName = row.original.surname
      return (
        <div className="flex items-center gap-2">
          <span
            className={cn("font-medium", !fullName && "text-muted-foreground")}
          >
            {fullName || "N/A"}
          </span>
          {row.original.isCurrentUser && (
            <Badge variant="outline" className="text-xs">
              Вы
            </Badge>
          )}
        </div>
      )
    },
  },
  {
    accessorKey: "middle_name",
    header: "Отчество",
    cell: ({ row }) => {
      const fullName = row.original.middle_name
      return (
        <div className="flex items-center gap-2">
          <span
            className={cn("font-medium", !fullName && "text-muted-foreground")}
          >
            {fullName || "N/A"}
          </span>
          {row.original.isCurrentUser && (
            <Badge variant="outline" className="text-xs">
              Вы
            </Badge>
          )}
        </div>
      )
    },
  },
  {
    accessorKey: "login",
    header: "Логин",
    cell: ({ row }) => (
      <span className="text-muted-foreground">{row.original.login}</span>
    ),
  },
  {
    accessorKey: "role",
    header: "Роль",
    cell: ({ row }) => (
      <span className="text-muted-foreground">
        {formatRoleName(row.original.role.name)}
      </span>
    ),
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Действия</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <UserActionsMenu user={row.original} />
      </div>
    ),
  },
]
