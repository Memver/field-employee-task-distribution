import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import { AgentPointEventsService } from "@/client"
import {
  type AgentPointEventTableData,
  columns,
} from "@/components/AgentPointEvent/columns"
import { DataTable } from "@/components/Common/DataTable"
import { queryKeys } from "@/lib/queryKeys"

function getAgentPointEventsQueryOptions() {
  return {
    queryFn: () =>
      AgentPointEventsService.readAgentPointEvents({ skip: 0, limit: 100 }),
    queryKey: queryKeys.agentPointEvents.all,
  }
}

export const Route = createFileRoute("/_layout/agent-point-events")({
  component: AgentPointEvents,
})

function AgentPointEvents() {
  const { data } = useSuspenseQuery(getAgentPointEventsQueryOptions())
  const tableData: AgentPointEventTableData[] = data.data

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            События агентских точек
          </h1>
          <p className="text-muted-foreground">
            Просмотр событий по агентским точкам
          </p>
        </div>
      </div>
      <DataTable columns={columns} data={tableData} />
    </div>
  )
}
