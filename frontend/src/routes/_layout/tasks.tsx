import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import AddTask from "@/components/Task/AddTask"
import { DataTable } from "@/components/Common/DataTable"
import { columns, type TaskTableData } from "@/components/Task/columns"
import { getAdminTasksQueryOptions } from "@/features/tasks/queries"

export const Route = createFileRoute("/_layout/tasks")({
  component: Tasks,
})

function Tasks() {
  const { data } = useSuspenseQuery(getAdminTasksQueryOptions())
  const tableData: TaskTableData[] = data.data
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Задачи</h1>
          <p className="text-muted-foreground">Управление задачами</p>
        </div>
        <AddTask />
      </div>
      <DataTable columns={columns} data={tableData} />
    </div>
  )
}

