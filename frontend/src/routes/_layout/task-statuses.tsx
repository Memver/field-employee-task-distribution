import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import { TaskStatusesService } from "@/client"
import AddTaskStatus from "@/components/TaskStatus/AddTaskStatus"
import { columns, type TaskStatusTableData } from "@/components/TaskStatus/columns"
import { DataTable } from "@/components/Common/DataTable"
import { queryKeys } from "@/lib/queryKeys"

function getTaskStatusesQueryOptions() {
  return {
    queryFn: () =>
      TaskStatusesService.readTaskStatuses({ skip: 0, limit: 100 }),
    queryKey: queryKeys.taskStatuses.all,
  }
}

export const Route = createFileRoute("/_layout/task-statuses")({
  component: TaskStatuses,
  head: () => ({
    meta: [
      {
        title: "Task Statuses - FastAPI Cloud",
      },
    ],
  }),
})

function TaskStatusesTableContent() {
  const { data: taskStatuses } = useSuspenseQuery(getTaskStatusesQueryOptions())

  const tableData: TaskStatusTableData[] = taskStatuses.data

  return <DataTable columns={columns} data={tableData} />
}

function TaskStatusesTable() {
  return <TaskStatusesTableContent />
}

function TaskStatuses() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Статусы задач</h1>
          <p className="text-muted-foreground">Управление статусами</p>
        </div>
        <AddTaskStatus />
      </div>
      <TaskStatusesTable />
    </div>
  )
}

