import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { DataTable } from "@/components/Common/DataTable"
import AddTaskCarryover from "@/components/TaskCarryover/AddTaskCarryover"
import {
  columns,
  type TaskCarryoverTableData,
} from "@/components/TaskCarryover/columns"
import { getTaskCarryoversQueryOptions } from "@/features/taskCarryovers/queries"
import { emptyTable, pageTitles } from "@/lib/i18n/ru"

export const Route = createFileRoute("/_layout/task-carryovers")({
  component: TaskCarryovers,
  head: () => ({
    meta: [{ title: pageTitles.taskCarryovers }],
  }),
})

function TaskCarryovers() {
  const { data } = useSuspenseQuery(getTaskCarryoversQueryOptions())
  const tableData: TaskCarryoverTableData[] = data.data

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Перенесенные задачи
          </h1>
          <p className="text-muted-foreground">
            Управление задачами, перенесенными на следующий день
          </p>
        </div>
        <AddTaskCarryover />
      </div>
      <DataTable
        columns={columns}
        data={tableData}
        emptyTitle={emptyTable.defaultTitle}
        emptyDescription={emptyTable.taskCarryovers}
      />
    </div>
  )
}
