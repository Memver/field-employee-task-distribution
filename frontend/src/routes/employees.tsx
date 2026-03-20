import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import { EmployeesService } from "@/client"
//import { columns, type EmployeeTableData } from "@/components/Employee/columns";
import { DataTable } from "@/components/Common/DataTable"
//import PendingEmployees from "@/components/Pending/PendingEmployees";
import useAuth from "@/hooks/useAuth"

function getEmployeesQueryOptions() {
  return {
    queryFn: () => EmployeesService.readEmployees({ skip: 0, limit: 100 }),
    queryKey: ["Employees"],
  }
}

export const Route = createFileRoute("/employees")({
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
  const { user: currentUser } = useAuth()
  const { data: Employees } = useSuspenseQuery(getEmployeesQueryOptions())

  const tableData: EmployeeTableData[] = Employees.data

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
          <h1 className="text-2xl font-bold tracking-tight">Employees</h1>
          <p className="text-muted-foreground">
            Manage Employee accounts and permissions
          </p>
        </div>
        {/* <AddEmployee /> */}
      </div>
      <EmployeesTable />
    </div>
  )
}
