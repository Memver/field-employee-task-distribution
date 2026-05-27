import type { ColumnDef } from "@tanstack/react-table"

import type { UserPublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import { formatRoleName } from "@/lib/i18n/ru"
import { cn } from "@/lib/utils"
import { UserActionsMenu } from "./UserActionsMenu"

export type UserTableData = UserPublic & {
  isCurrentUser: boolean
}

function NameCell({
  value,
  showCurrentUserBadge,
}: {
  value: string | undefined
  showCurrentUserBadge?: boolean
}) {
  return (
    <div className="flex items-center gap-2">
      <span className={cn("font-medium", !value && "text-muted-foreground")}>
        {value || "N/A"}
      </span>
      {showCurrentUserBadge && (
        <Badge variant="outline" className="text-xs">
          Вы
        </Badge>
      )}
    </div>
  )
}

export const columns: ColumnDef<UserTableData>[] = [
  {
    accessorKey: "surname",
    header: "Фамилия",
    cell: ({ row }) => (
      <NameCell
        value={row.original.surname}
        showCurrentUserBadge={row.original.isCurrentUser}
      />
    ),
  },
  {
    accessorKey: "name",
    header: "Имя",
    cell: ({ row }) => <NameCell value={row.original.name} />,
  },
  {
    accessorKey: "middle_name",
    header: "Отчество",
    cell: ({ row }) => <NameCell value={row.original.middle_name} />,
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
