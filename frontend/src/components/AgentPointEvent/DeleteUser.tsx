import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Trash2 } from "lucide-react"

import { AgentPointEventsService } from "@/client"
import { DropdownMenuItem } from "@/components/ui/dropdown-menu"
import useCustomToast from "@/hooks/useCustomToast"
import { toasts } from "@/lib/i18n/ru"
import { queryKeys } from "@/lib/queryKeys"
import { handleError } from "@/utils"

interface DeleteUserProps {
  id: number
  onSuccess: () => void
}

const DeleteUser = ({ id, onSuccess }: DeleteUserProps) => {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: () =>
      AgentPointEventsService.deleteAgentPointEvent({ agentPointEventId: id }),
    onSuccess: () => {
      showSuccessToast(toasts.agentPointEventDeleted)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.agentPointEvents.all })
    },
  })

  return (
    <DropdownMenuItem
      className="text-destructive focus:text-destructive"
      onSelect={(e) => {
        e.preventDefault()
        mutation.mutate()
      }}
      disabled={mutation.isPending}
    >
      <Trash2 className="mr-2 h-4 w-4" />
      Удалить
    </DropdownMenuItem>
  )
}

export default DeleteUser
