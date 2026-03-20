import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Pencil } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type EmployeePublic, type EmployeeUpdate, EmployeesService } from "@/client"
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
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const formSchema = z.object({
  user_id: z.coerce.number().int().positive(),
  grade_id: z.coerce.number().int().positive(),
  start_location_id: z.coerce.number().int().positive(),
})

type FormData = z.infer<typeof formSchema>

interface Props {
  employee: EmployeePublic
  onSuccess: () => void
}

const EditUser = ({ employee, onSuccess }: Props) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: employee,
    mode: "onBlur",
    criteriaMode: "all",
  })

  const mutation = useMutation({
    mutationFn: (data: EmployeeUpdate) =>
      EmployeesService.updateEmployee({ id: employee.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Employee updated successfully")
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["employees"] }),
  })

  const onSubmit = (data: FormData) => mutation.mutate(data)

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem onSelect={(e) => e.preventDefault()} onClick={() => setIsOpen(true)}>
        <Pencil /> Редактировать
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <DialogHeader><DialogTitle>Редактировать сотрудника</DialogTitle><DialogDescription>Обновите связанные id.</DialogDescription></DialogHeader>
            <div className="grid gap-4 py-4">
              <FormField control={form.control} name="user_id" render={({ field }) => (
                <FormItem><FormLabel>ID пользователя</FormLabel><FormControl><Input type="number" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
              <FormField control={form.control} name="grade_id" render={({ field }) => (
                <FormItem><FormLabel>ID грейда</FormLabel><FormControl><Input type="number" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
              <FormField control={form.control} name="start_location_id" render={({ field }) => (
                <FormItem><FormLabel>ID стартовой локации</FormLabel><FormControl><Input type="number" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
            </div>
            <DialogFooter>
              <DialogClose asChild><Button variant="outline" disabled={mutation.isPending}>Отменить</Button></DialogClose>
              <LoadingButton type="submit" loading={mutation.isPending}>Сохранить</LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default EditUser

