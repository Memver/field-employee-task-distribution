import { useQuery } from "@tanstack/react-query"
import { AgentPointsService, TaskTypesService } from "@/client"
import { toSelectOptions } from "@/components/Common/RelationSelect"
import { formatAgentPoint } from "@/lib/entityLabels"
import { formatTaskTypeName } from "@/lib/i18n/ru"

export function useTaskCarryoverFormOptions() {
  const agentPoints = useQuery({
    queryKey: ["agent-points", "carryover-form-options"],
    queryFn: () => AgentPointsService.readAgentPoints({ skip: 0, limit: 100 }),
  })
  const taskTypes = useQuery({
    queryKey: ["task-types", "carryover-form-options"],
    queryFn: () => TaskTypesService.readTaskTypes({ skip: 0, limit: 100 }),
  })

  return {
    isLoading: agentPoints.isLoading || taskTypes.isLoading,
    agentPointOptions: toSelectOptions(
      agentPoints.data?.data ?? [],
      (item) => item.id,
      (item) => formatAgentPoint(item),
    ),
    taskTypeOptions: toSelectOptions(
      taskTypes.data?.data ?? [],
      (item) => item.id,
      (item) => formatTaskTypeName(item.name),
    ),
  }
}
