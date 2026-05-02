import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import { AgentPointsService } from "@/client"
import AddUser from "@/components/AgentPoint/AddUser"
import {
  type AgentPointTableData,
  columns,
} from "@/components/AgentPoint/columns"
import { DataTable } from "@/components/Common/DataTable"

function getAgentPointsQueryOptions() {
  return {
    queryFn: () => AgentPointsService.readAgentPoints({ skip: 0, limit: 100 }),
    queryKey: ["agent-points"],
  }
}

export const Route = createFileRoute("/_layout/agent-points")({
  component: AgentPoints,
})

function AgentPoints() {
  const { data } = useSuspenseQuery(getAgentPointsQueryOptions())
  const tableData: AgentPointTableData[] = data.data
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Агентские точки</h1>
          <p className="text-muted-foreground">Управление агентскими точками</p>
        </div>
        <AddUser />
      </div>
      <DataTable columns={columns} data={tableData} />
    </div>
  )
}
