import { Trash2 } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
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
import { useDeleteTaskCarryoverMutation } from "@/features/taskCarryovers/mutations"

type Props = {
  id: number
  onSuccess: () => void
}

function DeleteTaskCarryover({ id, onSuccess }: Props) {
  const [isOpen, setIsOpen] = useState(false)
  const { handleSubmit } = useForm()
  const mutation = useDeleteTaskCarryoverMutation(() => {
    setIsOpen(false)
    onSuccess()
  })

  const onSubmit = () => {
    mutation.mutate(id)
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem
        variant="destructive"
        onSelect={(event) => event.preventDefault()}
        onClick={() => setIsOpen(true)}
      >
        <Trash2 />
        Удалить перенос
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Удалить перенос</DialogTitle>
            <DialogDescription>
              Перенесенная задача будет удалена из списка.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-4">
            <DialogClose asChild>
              <Button variant="outline" disabled={mutation.isPending}>
                Отмена
              </Button>
            </DialogClose>
            <LoadingButton
              variant="destructive"
              type="submit"
              loading={mutation.isPending}
            >
              Удалить
            </LoadingButton>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default DeleteTaskCarryover
