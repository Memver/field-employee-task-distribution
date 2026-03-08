import { useSuspenseQuery } from "@tanstack/react-query";
import { createFileRoute, redirect } from "@tanstack/react-router";
import { Suspense } from "react";

import { type LocationPublic, LocationsService } from "@/client";
import { columns, type LocationTableData } from "@/components/Location/columns";
import { DataTable } from "@/components/Common/DataTable";
import PendingLocations from "@/components/Pending/PendingLocations";
import useAuth from "@/hooks/useAuth";
import AddUser from "@/components/Admin/AddUser";
import { LoadingButton } from "@/components/ui/loading-button";

function getLocationsQueryOptions() {
  return {
    queryFn: () => LocationsService.readLocations({ skip: 0, limit: 100 }),
    queryKey: ["Locations"],
  };
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
});

function LocationsTableContent() {
  const { user: currentUser } = useAuth();
  const { data: Locations } = useSuspenseQuery(getLocationsQueryOptions());

  const tableData: LocationTableData[] = Locations.data;

  return <DataTable columns={columns} data={tableData} />;
}

function LocationsTable() {
  return <LocationsTableContent />;
}

function Location() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Локации</h1>
          <p className="text-muted-foreground">Управление локациями</p>
        </div>
        <LoadingButton type="submit">Добавить локацию</LoadingButton>
      </div>
      <LocationsTable />
    </div>
  );
}
