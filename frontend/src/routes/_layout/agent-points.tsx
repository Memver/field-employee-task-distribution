import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import { AgentPointsService } from "@/client"
import AddUser from "@/components/AgentPoint/AddUser"
import {
  type AgentPointTableData,
  getAgentPointColumns,
} from "@/components/AgentPoint/columns"
import { DataTable } from "@/components/Common/DataTable"
import { isAgentPointManagerRole } from "@/features/navigation/roleSections"
import useAuth from "@/hooks/useAuth"
import { emptyTable, pageTitles } from "@/lib/i18n/ru"
import { queryKeys } from "@/lib/queryKeys"

function getAgentPointsQueryOptions() {
  return {
    queryFn: () => AgentPointsService.readAgentPoints({ skip: 0, limit: 100 }),
    queryKey: queryKeys.agentPoints.all,
  }
}

export const Route = createFileRoute("/_layout/agent-points")({
  component: AgentPoints,
  head: () => ({
    meta: [
      {
        title: pageTitles.agentPoints,
      },
    ],
  }),
})

function AgentPoints() {
  const { user: currentUser } = useAuth()
  const isApm = isAgentPointManagerRole(currentUser?.role?.name)
  const { data } = useSuspenseQuery(getAgentPointsQueryOptions())
  const tableData: AgentPointTableData[] = data.data
  const columns = getAgentPointColumns(isApm)

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            {isApm ? "Мои агентские точки" : "Агентские точки"}
          </h1>
          <p className="text-muted-foreground">
            {isApm
              ? "Агентские точки под вашим управлением"
              : "Управление агентскими точками"}
          </p>
        </div>
        {!isApm && <AddUser />}
      </div>
      <DataTable
        columns={columns}
        data={tableData}
        emptyTitle={emptyTable.agentPoints}
      />
    </div>
  )
}
