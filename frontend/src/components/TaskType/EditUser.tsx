import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Pencil } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import {
  type TaskTypePublic,
  TaskTypesService,
  type TaskTypeUpdate,
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
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import { useTaskTypeFormOptions } from "@/features/taskTypes/formOptions"
import useCustomToast from "@/hooks/useCustomToast"
import { toasts } from "@/lib/i18n/ru"
import { queryKeys } from "@/lib/queryKeys"
import { handleError } from "@/utils"

const formSchema = z.object({
  name: z.string().min(1),
  execution_time: z.coerce.number().positive(),
  min_grade_id: z.coerce.number().int().positive(),
  priority_id: z.coerce.number().int().positive(),
})

type FormData = z.output<typeof formSchema>

interface Props {
  taskType: TaskTypePublic
  onSuccess: () => void
}

const EditUser = ({ taskType, onSuccess }: Props) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const options = useTaskTypeFormOptions()
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: taskType.name,
      execution_time: taskType.execution_time,
      min_grade_id: taskType.min_grade_id,
      priority_id: taskType.priority_id,
    },
    mode: "onBlur",
    criteriaMode: "all",
  })

  const mutation = useMutation({
    mutationFn: (data: TaskTypeUpdate) =>
      TaskTypesService.updateTaskType({ id: taskType.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast(toasts.taskTypeUpdated)
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () =>
      queryClient.invalidateQueries({ queryKey: queryKeys.taskTypes.all }),
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
              <DialogTitle>Редактировать тип задачи</DialogTitle>
              <DialogDescription>Обновите поля.</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Название</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="execution_time"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Время выполнения, часы (можно дробное)</FormLabel>
                    <FormControl>
                      <Input type="number" step="0.1" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="min_grade_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Мин. грейд</FormLabel>
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
                name="priority_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Приоритет</FormLabel>
                    <FormControl>
                      <RelationSelect
                        value={String(field.value)}
                        onChange={(v) => field.onChange(Number(v))}
                        options={options.priorityOptions}
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
