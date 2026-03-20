import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import { TasksService } from "@/client"
import AddUser from "@/components/Task/AddUser"
import { DataTable } from "@/components/Common/DataTable"
import { columns, type TaskTableData } from "@/components/Task/columns"

function getTasksQueryOptions() {
  return {
    queryFn: () => TasksService.readTasks({ skip: 0, limit: 100 }),
    queryKey: ["tasks-admin"],
  }
}

export const Route = createFileRoute("/_layout/tasks")({
  component: Tasks,
})

function Tasks() {
  const { data } = useSuspenseQuery(getTasksQueryOptions())
  const tableData: TaskTableData[] = data.data
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Задачи</h1>
          <p className="text-muted-foreground">Управление задачами</p>
        </div>
        <AddUser />
      </div>
      <DataTable columns={columns} data={tableData} />
    </div>
  )
}

