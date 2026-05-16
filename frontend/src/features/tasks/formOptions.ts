import { useQuery } from "@tanstack/react-query"
import {
  AgentPointsService,
  EmployeesService,
  TaskStatusesService,
  TaskTypesService,
} from "@/client"
import { toSelectOptions } from "@/components/Common/RelationSelect"
import {
  formatAgentPoint,
  formatEmployee,
} from "@/lib/entityLabels"

export function useTaskFormOptions() {
  const employees = useQuery({
    queryKey: ["employees", "form-options"],
    queryFn: () => EmployeesService.readEmployees({ skip: 0, limit: 100 }),
  })
  const taskTypes = useQuery({
    queryKey: ["task-types", "form-options"],
    queryFn: () => TaskTypesService.readTaskTypes({ skip: 0, limit: 100 }),
  })
  const agentPoints = useQuery({
    queryKey: ["agent-points", "form-options"],
    queryFn: () => AgentPointsService.readAgentPoints({ skip: 0, limit: 100 }),
  })
  const taskStatuses = useQuery({
    queryKey: ["task-statuses", "form-options"],
    queryFn: () => TaskStatusesService.readTaskStatuses({ skip: 0, limit: 100 }),
  })

  return {
    isLoading:
      employees.isLoading ||
      taskTypes.isLoading ||
      agentPoints.isLoading ||
      taskStatuses.isLoading,
    employeeOptions: toSelectOptions(
      employees.data?.data ?? [],
      (e) => e.id,
      (e) => formatEmployee(e),
    ),
    taskTypeOptions: toSelectOptions(
      taskTypes.data?.data ?? [],
      (t) => t.id,
      (t) => t.name,
    ),
    agentPointOptions: toSelectOptions(
      agentPoints.data?.data ?? [],
      (a) => a.id,
      (a) => formatAgentPoint(a),
    ),
    taskStatusOptions: toSelectOptions(
      taskStatuses.data?.data ?? [],
      (s) => s.id,
      (s) => s.name,
    ),
  }
}
