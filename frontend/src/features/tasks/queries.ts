import { TaskStatusesService, TasksService } from "@/client"
import { queryKeys } from "@/lib/queryKeys"

export function getAdminTasksQueryOptions() {
  return {
    queryFn: () => TasksService.readTasks({ skip: 0, limit: 100 }),
    queryKey: queryKeys.tasks.admin,
  }
}

export function getFieldEmployeeTasksQueryOptions() {
  return {
    queryFn: () => TasksService.readTasksMe({ skip: 0, limit: 100 }),
    queryKey: queryKeys.tasks.me,
  }
}

export function getTaskStatusesQueryOptions() {
  return {
    queryFn: () => TaskStatusesService.readTaskStatuses({ skip: 0, limit: 100 }),
    queryKey: queryKeys.taskStatuses.all,
  }
}
