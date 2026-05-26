import type { ColumnDef } from "@tanstack/react-table"

import type { AgentPointPublic } from "@/client"
import { formatLocation } from "@/lib/entityLabels"
import { formatDateTime } from "@/lib/formatDateTime"
import { UserActionsMenu } from "./UserActionsMenu"

export type AgentPointTableData = AgentPointPublic

export function getAgentPointColumns(
  readOnly: boolean,
): ColumnDef<AgentPointTableData>[] {
  const cols: ColumnDef<AgentPointTableData>[] = [
    {
      accessorKey: "created_time",
      header: "Создано",
      cell: ({ row }) => formatDateTime(row.original.created_time),
    },
    {
      id: "location",
      header: "Локация",
      cell: ({ row }) => formatLocation(row.original.location),
    },
  ]

  if (!readOnly) {
    cols.push({
      id: "actions",
      header: () => <span className="sr-only">Действия</span>,
      cell: ({ row }) => (
        <div className="flex justify-end">
          <UserActionsMenu agentPoint={row.original} />
        </div>
      ),
    })
  }

  return cols
}

export const columns = getAgentPointColumns(false)
