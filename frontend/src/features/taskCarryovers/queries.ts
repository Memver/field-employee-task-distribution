import { queryKeys } from "@/lib/queryKeys"
import { TaskCarryoversApi } from "./api"

export function getTaskCarryoversQueryOptions() {
  return {
    queryFn: () => TaskCarryoversApi.readTaskCarryovers(0, 100),
    queryKey: queryKeys.taskCarryovers.list,
  }
}
