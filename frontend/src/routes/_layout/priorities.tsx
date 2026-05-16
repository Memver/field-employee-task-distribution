import { useSuspenseQuery } from "@tanstack/react-query"
import { pageTitles } from "@/lib/i18n/ru"
import { createFileRoute } from "@tanstack/react-router"

import { PrioritiesService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddPriority from "@/components/Priority/AddUser"
import { columns, type PriorityTableData } from "@/components/Priority/columns"

function getPrioritiesQueryOptions() {
  return {
    queryFn: () => PrioritiesService.readPriorities({ skip: 0, limit: 100 }),
    queryKey: ["priorities"],
  }
}

export const Route = createFileRoute("/_layout/priorities")({
  component: Priorities,
  head: () => ({
    meta: [
      {
        title: pageTitles.priorities,
      },
    ],
  }),
})

function PrioritiesTableContent() {
  const { data: priorities } = useSuspenseQuery(getPrioritiesQueryOptions())

  const tableData: PriorityTableData[] = priorities.data

  return <DataTable columns={columns} data={tableData} />
}

function PrioritiesTable() {
  return <PrioritiesTableContent />
}

function Priorities() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Приоритеты</h1>
          <p className="text-muted-foreground">Управление приоритетами</p>
        </div>
        <AddPriority />
      </div>
      <PrioritiesTable />
    </div>
  )
}
