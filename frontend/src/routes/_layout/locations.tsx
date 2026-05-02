import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"

import { LocationsService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddLocation from "@/components/Location/AddLocation"
import { columns, type LocationTableData } from "@/components/Location/columns"

function getLocationsQueryOptions() {
  return {
    queryFn: () => LocationsService.readLocations({ skip: 0, limit: 100 }),
    queryKey: ["locations"],
  }
}

export const Route = createFileRoute("/_layout/locations")({
  component: Location,
  head: () => ({
    meta: [
      {
        title: "Location - FastAPI Cloud",
      },
    ],
  }),
})

function LocationsTableContent() {
  const { data: locations } = useSuspenseQuery(getLocationsQueryOptions())

  const tableData: LocationTableData[] = locations.data

  return <DataTable columns={columns} data={tableData} />
}

function LocationsTable() {
  return <LocationsTableContent />
}

function Location() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Локации</h1>
          <p className="text-muted-foreground">Управление локациями</p>
        </div>
        <AddLocation />
      </div>
      <LocationsTable />
    </div>
  )
}
