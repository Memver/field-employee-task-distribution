import { useMutation, useQueryClient } from "@tanstack/react-query"
import { TasksService, type TaskSelfUpdate } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { toasts } from "@/lib/i18n/ru"
import { queryKeys } from "@/lib/queryKeys"
import { handleError } from "@/utils"

type UpdateMyTaskStatusPayload = {
  taskId: number
  requestBody: TaskSelfUpdate
}

export function useUpdateMyTaskStatusMutation() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: ({ taskId, requestBody }: UpdateMyTaskStatusPayload) =>
      TasksService.updateMyTaskStatus({ taskId, requestBody }),
    onSuccess: () => {
      showSuccessToast(toasts.taskStatusUpdatedField)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.me })
    },
  })
}
