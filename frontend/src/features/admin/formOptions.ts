import { useQuery } from "@tanstack/react-query"
import { RolesService } from "@/client"
import { toSelectOptions } from "@/components/Common/RelationSelect"
import { formatRoleName } from "@/lib/i18n/ru"

export function useAdminFormOptions() {
  const roles = useQuery({
    queryKey: ["roles", "form-options"],
    queryFn: () => RolesService.readRoles({ skip: 0, limit: 100 }),
  })

  return {
    isLoading: roles.isLoading,
    roleOptions: toSelectOptions(
      roles.data?.data ?? [],
      (r) => r.id,
      (r) => formatRoleName(r.name),
    ),
  }
}
