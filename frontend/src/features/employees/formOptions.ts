import { useQuery } from "@tanstack/react-query"
import { GradesService, LocationsService, UsersService } from "@/client"
import { toSelectOptions } from "@/components/Common/RelationSelect"
import { formatLocation, formatUserRef } from "@/lib/entityLabels"
import { formatGradeName } from "@/lib/i18n/ru"

export function useEmployeeFormOptions() {
  const users = useQuery({
    queryKey: ["users", "for-employee-form"],
    queryFn: () => UsersService.readUsersForEmployeeForm({ skip: 0, limit: 100 }),
  })
  const grades = useQuery({
    queryKey: ["grades", "form-options"],
    queryFn: () => GradesService.readGrades({ skip: 0, limit: 100 }),
  })
  const locations = useQuery({
    queryKey: ["locations", "form-options"],
    queryFn: () => LocationsService.readLocations({ skip: 0, limit: 100 }),
  })

  return {
    isLoading: users.isLoading || grades.isLoading || locations.isLoading,
    userOptions: toSelectOptions(
      users.data?.data ?? [],
      (u) => u.id,
      (u) => formatUserRef(u),
    ),
    gradeOptions: toSelectOptions(
      grades.data?.data ?? [],
      (g) => g.id,
      (g) => formatGradeName(g.name),
    ),
    locationOptions: toSelectOptions(
      locations.data?.data ?? [],
      (l) => l.id,
      (l) => formatLocation(l),
    ),
  }
}
