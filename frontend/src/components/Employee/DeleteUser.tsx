import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Trash2 } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"

import { EmployeesService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { DropdownMenuItem } from "@/components/ui/dropdown-menu"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface Props {
  id: number
  onSuccess: () => void
}

const DeleteUser = ({ id, onSuccess }: Props) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { handleSubmit } = useForm()

  const mutation = useMutation({
    mutationFn: (employeeId: number) =>
      EmployeesService.deleteEmployee({ employeeId }),
    onSuccess: () => {
      showSuccessToast("Employee deleted successfully")
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["employees"] }),
  })

  const onSubmit = async () => mutation.mutate(id)

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem variant="destructive" onSelect={(e) => e.preventDefault()} onClick={() => setIsOpen(true)}>
        <Trash2 /> Удалить
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader><DialogTitle>Удалить сотрудника</DialogTitle><DialogDescription>Действие нельзя отменить.</DialogDescription></DialogHeader>
          <DialogFooter className="mt-4">
            <DialogClose asChild><Button variant="outline" disabled={mutation.isPending}>Отмена</Button></DialogClose>
            <LoadingButton variant="destructive" type="submit" loading={mutation.isPending}>Удалить</LoadingButton>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default DeleteUser

