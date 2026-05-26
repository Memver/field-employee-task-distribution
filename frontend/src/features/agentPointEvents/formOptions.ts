import { useSuspenseQuery } from "@tanstack/react-query"

import { AgentPointsService } from "@/client"
import { toSelectOptions } from "@/components/Common/RelationSelect"
import { formatAgentPoint } from "@/lib/entityLabels"
import { queryKeys } from "@/lib/queryKeys"

export function useAgentPointEventFormOptions() {
  const { data: agentPoints } = useSuspenseQuery({
    queryKey: queryKeys.agentPoints.all,
    queryFn: () => AgentPointsService.readAgentPoints({ skip: 0, limit: 100 }),
  })

  const agentPointOptions = toSelectOptions(
    agentPoints.data,
    (point) => point.id,
    (point) => formatAgentPoint(point),
  )

  return {
    agentPointOptions,
    isLoading: false,
  }
}
