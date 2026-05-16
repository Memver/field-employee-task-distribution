import type { ColumnDef } from "@tanstack/react-table"

import type { AgentPointPublic } from "@/client"
import { formatLocation } from "@/lib/entityLabels"
import { UserActionsMenu } from "./UserActionsMenu"

export type AgentPointTableData = AgentPointPublic

export const columns: ColumnDef<AgentPointTableData>[] = [
  { accessorKey: "created_time", header: "Создано" },
  { accessorKey: "is_cards_delivered", header: "Карты доставлены" },
  {
    accessorKey: "days_since_last_card_gived",
    header: "Дней с последней выдачи",
  },
  { accessorKey: "approved_applications", header: "Одобренные заявки" },
  { accessorKey: "cards_gived", header: "Выдано карт" },
  {
    id: "location",
    header: "Локация",
    cell: ({ row }) => formatLocation(row.original.location),
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Действия</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <UserActionsMenu agentPoint={row.original} />
      </div>
    ),
  },
]
