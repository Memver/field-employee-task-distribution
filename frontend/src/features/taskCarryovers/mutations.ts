import { useMutation, useQueryClient } from "@tanstack/react-query"
import useCustomToast from "@/hooks/useCustomToast"
import { toasts } from "@/lib/i18n/ru"
import { queryKeys } from "@/lib/queryKeys"
import { handleError } from "@/utils"
import { TaskCarryoversApi } from "./api"
import type { TaskCarryoverCreate, TaskCarryoverUpdate } from "./types"

export function useCreateTaskCarryoverMutation(onSuccess?: () => void) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: (requestBody: TaskCarryoverCreate) =>
      TaskCarryoversApi.createTaskCarryover(requestBody),
    onSuccess: () => {
      showSuccessToast(toasts.taskCarryoverCreated)
      onSuccess?.()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.taskCarryovers.list })
    },
  })
}

export function useUpdateTaskCarryoverMutation(onSuccess?: () => void) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: ({
      taskCarryoverId,
      requestBody,
    }: {
      taskCarryoverId: number
      requestBody: TaskCarryoverUpdate
    }) => TaskCarryoversApi.updateTaskCarryover(taskCarryoverId, requestBody),
    onSuccess: () => {
      showSuccessToast(toasts.taskCarryoverUpdated)
      onSuccess?.()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.taskCarryovers.list })
    },
  })
}

export function useDeleteTaskCarryoverMutation(onSuccess?: () => void) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: (taskCarryoverId: number) =>
      TaskCarryoversApi.deleteTaskCarryover(taskCarryoverId),
    onSuccess: () => {
      showSuccessToast(toasts.taskCarryoverDeleted)
      onSuccess?.()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.taskCarryovers.list })
    },
  })
}
