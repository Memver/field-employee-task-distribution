import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import { AgentPointEventsService } from "@/client"
import AddUser from "@/components/AgentPointEvent/AddUser"
import {
  type AgentPointEventTableData,
  columns,
} from "@/components/AgentPointEvent/columns"
import { DataTable } from "@/components/Common/DataTable"
import { isAgentPointManagerRole } from "@/features/navigation/roleSections"
import useAuth from "@/hooks/useAuth"
import { emptyTable, pageTitles } from "@/lib/i18n/ru"
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
  head: () => ({
    meta: [
      {
        title: pageTitles.agentPointEvents,
      },
    ],
  }),
})

function AgentPointEvents() {
  const { user: currentUser } = useAuth()
  const isApm = isAgentPointManagerRole(currentUser?.role?.name)
  const { data } = useSuspenseQuery(getAgentPointEventsQueryOptions())
  const tableData: AgentPointEventTableData[] = data.data

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            {isApm ? "Мои события" : "События агентских точек"}
          </h1>
          <p className="text-muted-foreground">
            {isApm
              ? "События по вашим агентским точкам"
              : "Просмотр и управление событиями"}
          </p>
        </div>
        <AddUser />
      </div>
      <DataTable
        columns={columns}
        data={tableData}
        emptyTitle={emptyTable.agentPointEvents}
      />
    </div>
  )
}
