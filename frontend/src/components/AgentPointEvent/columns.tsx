import type { ColumnDef } from "@tanstack/react-table"

import type { AgentPointEventPublic } from "@/client"
import { formatAgentPoint } from "@/lib/entityLabels"
import { formatDateTime } from "@/lib/formatDateTime"
import {
  formatBoolean,
  formatEventTypeName,
  formatMetricName,
} from "@/lib/i18n/ru"
import { UserActionsMenu } from "./UserActionsMenu"

export type AgentPointEventTableData = AgentPointEventPublic

export const columns: ColumnDef<AgentPointEventTableData>[] = [
  {
    id: "agent_point",
    header: "Агентская точка",
    cell: ({ row }) => formatAgentPoint(row.original.agent_point),
  },
  {
    accessorKey: "event_time",
    header: "Время события",
    cell: ({ row }) => formatDateTime(row.original.event_time),
  },
  {
    accessorKey: "event_type",
    header: "Тип события",
    cell: ({ row }) => formatEventTypeName(row.original.event_type),
  },
  {
    accessorKey: "metric_name",
    header: "Метрика",
    cell: ({ row }) => formatMetricName(row.original.metric_name ?? undefined),
  },
  {
    accessorKey: "metric_delta",
    header: "Изменение",
    cell: ({ row }) => row.original.metric_delta ?? "—",
  },
  {
    accessorKey: "metric_value_num",
    header: "Значение (число)",
    cell: ({ row }) => row.original.metric_value_num ?? "—",
  },
  {
    accessorKey: "metric_value_bool",
    header: "Значение (да/нет)",
    cell: ({ row }) => formatBoolean(row.original.metric_value_bool),
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Действия</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <UserActionsMenu event={row.original} />
      </div>
    ),
  },
]
