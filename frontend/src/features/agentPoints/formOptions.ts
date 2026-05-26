import { useQuery } from "@tanstack/react-query"
import { LocationsService } from "@/client"
import { toSelectOptions } from "@/components/Common/RelationSelect"
import { formatLocation } from "@/lib/entityLabels"

export function useAgentPointFormOptions() {
  const locations = useQuery({
    queryKey: ["locations", "form-options"],
    queryFn: () => LocationsService.readLocations({ skip: 0, limit: 100 }),
  })

  return {
    isLoading: locations.isLoading,
    locationOptions: toSelectOptions(
      locations.data?.data ?? [],
      (l) => l.id,
      (l) => formatLocation(l),
    ),
  }
}
