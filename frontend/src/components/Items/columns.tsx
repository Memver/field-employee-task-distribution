import type { ColumnDef } from "@tanstack/react-table"

import type { ItemPublic } from "@/client"
import { cn } from "@/lib/utils"
import { ItemActionsMenu } from "./ItemActionsMenu"

export const columns: ColumnDef<ItemPublic>[] = [
  {
    accessorKey: "title",
    header: "Название",
    cell: ({ row }) => (
      <span className="font-medium">{row.original.title}</span>
    ),
  },
  {
    accessorKey: "description",
    header: "Описание",
    cell: ({ row }) => {
      const description = row.original.description
      return (
        <span
          className={cn(
            "max-w-xs truncate block text-muted-foreground",
            !description && "italic",
          )}
        >
          {description || "Нет описания"}
        </span>
      )
    },
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <ItemActionsMenu item={row.original} />
      </div>
    ),
  },
]
