import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Plus } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type TaskCreate, TasksService } from "@/client"
import {
  RelationSelect,
} from "@/components/Common/RelationSelect"
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
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import { useTaskFormOptions } from "@/features/tasks/formOptions"
import useCustomToast from "@/hooks/useCustomToast"
import { toasts } from "@/lib/i18n/ru"
import { queryKeys } from "@/lib/queryKeys"
import { handleError } from "@/utils"

const formSchema = z.object({
  start_time: z.string().min(1),
  finish_time: z.string().min(1),
  comment: z.string().optional(),
  employee_id: z.coerce.number().int().positive(),
  task_type_id: z.coerce.number().int().positive(),
  agent_point_id: z.coerce.number().int().positive(),
  task_status_id: z.coerce.number().int().positive(),
})

type FormData = z.output<typeof formSchema>

const toIsoDateTime = (value: string) => new Date(value).toISOString()

type AddUserProps = {
  disabled?: boolean
}

const AddUser = ({ disabled = false }: AddUserProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const options = useTaskFormOptions()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
  })

  const mutation = useMutation({
    mutationFn: (data: TaskCreate) =>
      TasksService.createTask({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast(toasts.taskCreated)
      form.reset()
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.admin })
    },
  })

  const onSubmit = (data: FormData) => {
    mutation.mutate({
      ...data,
      comment: data.comment?.trim() || "",
      start_time: toIsoDateTime(data.start_time),
      finish_time: toIsoDateTime(data.finish_time),
    })
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className="my-4" disabled={disabled}>
          <Plus className="mr-2" />
          Добавить задачу
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Добавить задачу</DialogTitle>
          <DialogDescription>Заполните данные новой задачи.</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="start_time"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Время начала</FormLabel>
                    <FormControl>
                      <Input type="datetime-local" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="finish_time"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Время окончания</FormLabel>
                    <FormControl>
                      <Input type="datetime-local" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="comment"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Комментарий</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Комментарий (необязательно)"
                        type="text"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="employee_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Сотрудник</FormLabel>
                    <FormControl>
                      <RelationSelect
                        value={field.value ? String(field.value) : ""}
                        onChange={(v) => field.onChange(Number(v))}
                        options={options.employeeOptions}
                        placeholder="Выберите сотрудника"
                        disabled={options.isLoading}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="task_type_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Тип задачи</FormLabel>
                    <FormControl>
                      <RelationSelect
                        value={field.value ? String(field.value) : ""}
                        onChange={(v) => field.onChange(Number(v))}
                        options={options.taskTypeOptions}
                        placeholder="Выберите тип"
                        disabled={options.isLoading}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="agent_point_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Агентская точка</FormLabel>
                    <FormControl>
                      <RelationSelect
                        value={field.value ? String(field.value) : ""}
                        onChange={(v) => field.onChange(Number(v))}
                        options={options.agentPointOptions}
                        placeholder="Выберите точку"
                        disabled={options.isLoading}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="task_status_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Статус</FormLabel>
                    <FormControl>
                      <RelationSelect
                        value={field.value ? String(field.value) : ""}
                        onChange={(v) => field.onChange(Number(v))}
                        options={options.taskStatusOptions}
                        placeholder="Выберите статус"
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
