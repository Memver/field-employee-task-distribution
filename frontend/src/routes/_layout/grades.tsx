import { useSuspenseQuery } from "@tanstack/react-query"
import { pageTitles } from "@/lib/i18n/ru"
import { createFileRoute } from "@tanstack/react-router"

import { GradesService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddGrade from "@/components/Grade/AddUser"
import { columns, type GradeTableData } from "@/components/Grade/columns"

function getGradesQueryOptions() {
  return {
    queryFn: () => GradesService.readGrades({ skip: 0, limit: 100 }),
    queryKey: ["grades"],
  }
}

export const Route = createFileRoute("/_layout/grades")({
  component: Grades,
  head: () => ({
    meta: [
      {
        title: pageTitles.grades,
      },
    ],
  }),
})

function GradesTableContent() {
  const { data: grades } = useSuspenseQuery(getGradesQueryOptions())

  const tableData: GradeTableData[] = grades.data

  return <DataTable columns={columns} data={tableData} />
}

function GradesTable() {
  return <GradesTableContent />
}

function Grades() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Грейды</h1>
          <p className="text-muted-foreground">Управление грейдами</p>
        </div>
        <AddGrade />
      </div>
      <GradesTable />
    </div>
  )
}
