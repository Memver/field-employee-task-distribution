import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import { EmployeesService } from "@/client"
import AddUser from "@/components/Employee/AddUser"
import { DataTable } from "@/components/Common/DataTable"
import { columns, type EmployeeTableData } from "@/components/Employee/columns"

function getEmployeesQueryOptions() {
  return {
    queryFn: () => EmployeesService.readEmployees({ skip: 0, limit: 100 }),
    queryKey: ["employees"],
  }
}

export const Route = createFileRoute("/_layout/employees")({
  component: Employee,
  head: () => ({
    meta: [
      {
        title: "Employee - FastAPI Cloud",
      },
    ],
  }),
})

function EmployeesTableContent() {
  const { data: employees } = useSuspenseQuery(getEmployeesQueryOptions())
  const tableData: EmployeeTableData[] = employees.data
  return <DataTable columns={columns} data={tableData} />
}

function EmployeesTable() {
  return <EmployeesTableContent />
}

function Employee() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Сотрудники</h1>
          <p className="text-muted-foreground">Управление сотрудниками</p>
        </div>
        <AddUser />
      </div>
      <EmployeesTable />
    </div>
  )
}

