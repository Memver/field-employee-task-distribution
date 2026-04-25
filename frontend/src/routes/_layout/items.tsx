import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Suspense } from "react"

import { DataTable } from "@/components/Common/DataTable"
import AddItem from "@/components/Items/AddItem"
import { columns } from "@/components/Items/columns"
import PendingItems from "@/components/Pending/PendingItems"
import { EmptyState } from "@/components/Common/EmptyState"
import { getItemsQueryOptions } from "@/features/items/queries"


export const Route = createFileRoute("/_layout/items")({
  component: Items,
  head: () => ({
    meta: [
      {
        title: "Items - FastAPI Cloud",
      },
    ],
  }),
})

function ItemsTableContent() {
  const { data: items } = useSuspenseQuery(getItemsQueryOptions())

  if (items.data.length === 0) {
    return (
      <EmptyState
        title="You don't have any items yet"
        description="Add a new item to get started"
      />
    )
  }

  return <DataTable columns={columns} data={items.data} />
}

function ItemsTable() {
  return (
    <Suspense fallback={<PendingItems />}>
      <ItemsTableContent />
    </Suspense>
  )
}

function Items() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Items</h1>
          <p className="text-muted-foreground">Create and manage your items</p>
        </div>
        <AddItem />
      </div>
      <ItemsTable />
    </div>
  )
}
