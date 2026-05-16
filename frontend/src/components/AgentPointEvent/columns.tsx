import type { ColumnDef } from "@tanstack/react-table"

import type { AgentPointEventPublic } from "@/client"
import { formatAgentPoint } from "@/lib/entityLabels"

export type AgentPointEventTableData = AgentPointEventPublic

export const columns: ColumnDef<AgentPointEventTableData>[] = [
  {
    id: "agent_point",
    header: "Агентская точка",
    cell: ({ row }) => formatAgentPoint(row.original.agent_point),
  },
  { accessorKey: "event_time", header: "Время события" },
  { accessorKey: "event_type", header: "Тип события" },
  { accessorKey: "metric_name", header: "Метрика" },
  { accessorKey: "metric_delta", header: "Изменение" },
  { accessorKey: "metric_value_num", header: "Значение (число)" },
  { accessorKey: "metric_value_bool", header: "Значение (да/нет)" },
]
