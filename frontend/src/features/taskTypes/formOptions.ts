import { useQuery } from "@tanstack/react-query"
import { GradesService, PrioritiesService } from "@/client"
import { toSelectOptions } from "@/components/Common/RelationSelect"

export function useTaskTypeFormOptions() {
  const grades = useQuery({
    queryKey: ["grades", "form-options"],
    queryFn: () => GradesService.readGrades({ skip: 0, limit: 100 }),
  })
  const priorities = useQuery({
    queryKey: ["priorities", "form-options"],
    queryFn: () => PrioritiesService.readPriorities({ skip: 0, limit: 100 }),
  })

  return {
    isLoading: grades.isLoading || priorities.isLoading,
    gradeOptions: toSelectOptions(
      grades.data?.data ?? [],
      (g) => g.id,
      (g) => g.name,
    ),
    priorityOptions: toSelectOptions(
      priorities.data?.data ?? [],
      (p) => p.id,
      (p) => p.name,
    ),
  }
}
