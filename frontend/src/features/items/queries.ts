import { ItemsService } from "@/client"
import { queryKeys } from "@/lib/queryKeys"

export function getItemsQueryOptions() {
  return {
    queryFn: () => ItemsService.readItems({ skip: 0, limit: 100 }),
    queryKey: queryKeys.items.all,
  }
}
