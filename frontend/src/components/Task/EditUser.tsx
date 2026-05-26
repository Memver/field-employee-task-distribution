import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Pencil } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type TaskPublic, TasksService, type TaskUpdate } from "@/client"
import { DateTimeField } from "@/components/Common/DateTimeField"
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
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import { useTaskFormOptions } from "@/features/tasks/formOptions"
import useCustomToast from "@/hooks/useCustomToast"
import { fromDateTimeLocalToUtcIso, toDateTimeLocalUtc } from "@/lib/dateTimeUtc"
import { toasts, validation } from "@/lib/i18n/ru"
import { queryKeys } from "@/lib/queryKeys"
import { handleError } from "@/utils"

const formSchema = z.object({
  start_time: z.string().min(1, { message: validation.required }),
  finish_time: z.string().min(1, { message: validation.required }),
  comment: z.string().optional(),
  employee_id: z.coerce.number().int().positive({ message: validation.invalidNumber }),
  task_type_id: z.coerce.number().int().positive({ message: validation.invalidNumber }),
  agent_point_id: z.coerce.number().int().positive({ message: validation.invalidNumber }),
  task_status_id: z.coerce.number().int().positive({ message: validation.invalidNumber }),
})

type FormData = z.output<typeof formSchema>

interface EditUserProps {
  task: TaskPublic
  onSuccess: () => void
}

const EditUser = ({ task, onSuccess }: EditUserProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const options = useTaskFormOptions()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      start_time: toDateTimeLocalUtc(task.start_time),
      finish_time: toDateTimeLocalUtc(task.finish_time),
      comment: task.comment ?? "",
      employee_id: task.employee_id,
      task_type_id: task.task_type_id,
      agent_point_id: task.agent_point_id,
      task_status_id: task.task_status_id,
    },
    mode: "onBlur",
    criteriaMode: "all",
  })

  const mutation = useMutation({
    mutationFn: (data: TaskUpdate) =>
      TasksService.updateTask({ id: task.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast(toasts.taskUpdated)
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () =>
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.admin }),
  })

  const onSubmit = (data: FormData) => {
    const start_time = fromDateTimeLocalToUtcIso(data.start_time)
    const finish_time = fromDateTimeLocalToUtcIso(data.finish_time)
    if (!start_time || !finish_time) {
      showErrorToast(validation.invalidDateTime)
      return
    }
    mutation.mutate({
      ...data,
      comment: data.comment?.trim() || "",
      start_time,
      finish_time,
    })
  }

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
              <DialogTitle>Редактировать задачу</DialogTitle>
              <DialogDescription>Обновите данные задачи</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="employee_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Сотрудник</FormLabel>
                    <FormControl>
                      <RelationSelect
                        value={String(field.value)}
                        onChange={(v) => field.onChange(Number(v))}
                        options={options.employeeOptions}
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
                        value={String(field.value)}
                        onChange={(v) => field.onChange(Number(v))}
                        options={options.taskTypeOptions}
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
                        value={String(field.value)}
                        onChange={(v) => field.onChange(Number(v))}
                        options={options.agentPointOptions}
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
                        value={String(field.value)}
                        onChange={(v) => field.onChange(Number(v))}
                        options={options.taskStatusOptions}
                        disabled={options.isLoading}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="start_time"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Время начала</FormLabel>
                    <FormControl>
                      <DateTimeField
                        value={field.value}
                        onChange={field.onChange}
                      />
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
                      <DateTimeField
                        value={field.value}
                        onChange={field.onChange}
                      />
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
                        {...field}
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
