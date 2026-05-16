import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Pencil } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import {
  type EmployeePublic,
  EmployeesService,
  type EmployeeUpdate,
} from "@/client"
import { RelationSelect } from "@/components/Common/RelationSelect"
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
import { LoadingButton } from "@/components/ui/loading-button"
import { useEmployeeFormOptions } from "@/features/employees/formOptions"
import useCustomToast from "@/hooks/useCustomToast"
import { toasts } from "@/lib/i18n/ru"
import { handleError } from "@/utils"

const formSchema = z.object({
  user_id: z.coerce.number().int().positive(),
  grade_id: z.coerce.number().int().positive(),
  start_location_id: z.coerce.number().int().positive(),
})

type FormData = z.output<typeof formSchema>

interface Props {
  employee: EmployeePublic
  onSuccess: () => void
}

const EditUser = ({ employee, onSuccess }: Props) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const options = useEmployeeFormOptions()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      user_id: employee.user_id,
      grade_id: employee.grade_id,
      start_location_id: employee.start_location_id,
    },
    mode: "onBlur",
    criteriaMode: "all",
  })

  const mutation = useMutation({
    mutationFn: (data: EmployeeUpdate) =>
      EmployeesService.updateEmployee({ id: employee.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast(toasts.employeeUpdated)
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["employees"] }),
  })

  const onSubmit = (data: FormData) => mutation.mutate(data)

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem
        onSelect={(e) => e.preventDefault()}
        onClick={() => setIsOpen(true)}
      >
        <Pencil /> Редактировать
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <DialogHeader>
              <DialogTitle>Редактировать сотрудника</DialogTitle>
              <DialogDescription>
                Обновите пользователя, грейд и стартовую локацию.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="user_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Пользователь</FormLabel>
                    <FormControl>
                      <RelationSelect
                        value={String(field.value)}
                        onChange={(v) => field.onChange(Number(v))}
                        options={options.userOptions}
                        disabled={options.isLoading}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="grade_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Грейд</FormLabel>
                    <FormControl>
                      <RelationSelect
                        value={String(field.value)}
                        onChange={(v) => field.onChange(Number(v))}
                        options={options.gradeOptions}
                        disabled={options.isLoading}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="start_location_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Стартовая локация</FormLabel>
                    <FormControl>
                      <RelationSelect
                        value={String(field.value)}
                        onChange={(v) => field.onChange(Number(v))}
                        options={options.locationOptions}
                        disabled={options.isLoading}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <Button variant="outline" disabled={mutation.isPending}>
                  Отменить
                </Button>
              </DialogClose>
              <LoadingButton type="submit" loading={mutation.isPending}>
                Сохранить
              </LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default EditUser
