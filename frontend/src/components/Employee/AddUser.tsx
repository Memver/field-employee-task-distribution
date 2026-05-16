import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Plus } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type EmployeeCreate, EmployeesService } from "@/client"
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
  DialogTrigger,
} from "@/components/ui/dialog"
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

const AddUser = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const options = useEmployeeFormOptions()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
  })

  const mutation = useMutation({
    mutationFn: (data: EmployeeCreate) =>
      EmployeesService.createEmployee({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast(toasts.employeeCreated)
      form.reset()
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["employees"] }),
  })

  const onSubmit = (data: FormData) => mutation.mutate(data)

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className="my-4">
          <Plus className="mr-2" />
          Добавить сотрудника
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Добавить сотрудника</DialogTitle>
          <DialogDescription>Выберите пользователя, грейд и стартовую локацию.</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="user_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Пользователь</FormLabel>
                    <FormControl>
                      <RelationSelect
                        value={field.value ? String(field.value) : ""}
                        onChange={(v) => field.onChange(Number(v))}
                        options={options.userOptions}
                        placeholder="Выберите пользователя"
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
                        value={field.value ? String(field.value) : ""}
                        onChange={(v) => field.onChange(Number(v))}
                        options={options.gradeOptions}
                        placeholder="Выберите грейд"
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
                        value={field.value ? String(field.value) : ""}
                        onChange={(v) => field.onChange(Number(v))}
                        options={options.locationOptions}
                        placeholder="Выберите локацию"
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

export default AddUser
