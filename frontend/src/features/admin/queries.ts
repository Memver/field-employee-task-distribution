import { UsersService } from "@/client"
import { queryKeys } from "@/lib/queryKeys"

export function getUsersQueryOptions() {
  return {
    queryFn: () => UsersService.readUsers({ skip: 0, limit: 100 }),
    queryKey: queryKeys.users.all,
  }
}
