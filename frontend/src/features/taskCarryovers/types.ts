import type { AgentPointPublic, TaskTypePublic } from "@/client"

export type TaskCarryoverPublic = {
  id: number
  carryover_days: number
  planned_for_date: string
  source_reason: string
  created_at: string
  updated_at: string
  agent_point_id: number
  task_type_id: number
  agent_point: AgentPointPublic
  task_type: TaskTypePublic
}

export type TaskCarryoversPublic = {
  data: TaskCarryoverPublic[]
  count: number
}

export type TaskCarryoverCreate = {
  carryover_days: number
  planned_for_date: string
  source_reason: string
  agent_point_id: number
  task_type_id: number
}

export type TaskCarryoverUpdate = TaskCarryoverCreate
