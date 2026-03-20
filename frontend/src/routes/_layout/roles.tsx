import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import { RolesService } from "@/client"
import AddRole from "@/components/Role/AddRole"
import { columns, type RoleTableData } from "@/components/Role/columns"
import { DataTable } from "@/components/Common/DataTable"

function getRolesQueryOptions() {
  return {
    queryFn: () => RolesService.readRoles({ skip: 0, limit: 100 }),
    queryKey: ["roles"],
  }
}

export const Route = createFileRoute("/_layout/roles")({
  component: Roles,
  head: () => ({
    meta: [
      {
        title: "Roles - FastAPI Cloud",
      },
    ],
  }),
})

function RolesTableContent() {
  const { data: roles } = useSuspenseQuery(getRolesQueryOptions())

  const tableData: RoleTableData[] = roles.data

  return <DataTable columns={columns} data={tableData} />
}

function RolesTable() {
  return <RolesTableContent />
}

function Roles() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Роли</h1>
          <p className="text-muted-foreground">Управление ролями</p>
        </div>
        <AddRole />
      </div>
      <RolesTable />
    </div>
  )
}

