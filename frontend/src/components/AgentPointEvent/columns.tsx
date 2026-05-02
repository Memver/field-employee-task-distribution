import type { ColumnDef } from "@tanstack/react-table"

import type { AgentPointEventPublic } from "@/client"

export type AgentPointEventTableData = AgentPointEventPublic

export const columns: ColumnDef<AgentPointEventTableData>[] = [
  { accessorKey: "id", header: "ID" },
  { accessorKey: "agent_point_id", header: "ID агентской точки" },
  { accessorKey: "event_time", header: "Время события" },
  { accessorKey: "event_type", header: "Тип события" },
  { accessorKey: "metric_name", header: "Метрика" },
  { accessorKey: "metric_delta", header: "Изменение" },
  { accessorKey: "metric_value_num", header: "Значение (число)" },
  { accessorKey: "metric_value_bool", header: "Значение (да/нет)" },
]
