import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import { TaskTypesService } from "@/client"
import AddUser from "@/components/TaskType/AddUser"
import { DataTable } from "@/components/Common/DataTable"
import { columns, type TaskTypeTableData } from "@/components/TaskType/columns"

function getTaskTypesQueryOptions() {
  return {
    queryFn: () => TaskTypesService.readTaskTypes({ skip: 0, limit: 100 }),
    queryKey: ["task-types"],
  }
}

export const Route = createFileRoute("/_layout/task-types")({
  component: TaskTypes,
})

function TaskTypesTableContent() {
  const { data } = useSuspenseQuery(getTaskTypesQueryOptions())
  const tableData: TaskTypeTableData[] = data.data
  return <DataTable columns={columns} data={tableData} />
}

function TaskTypes() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Типы задач</h1>
          <p className="text-muted-foreground">Управление типами задач</p>
        </div>
        <AddUser />
      </div>
      <TaskTypesTableContent />
    </div>
  )
}

