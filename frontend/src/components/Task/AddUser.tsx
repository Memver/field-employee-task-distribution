import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Plus } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type TaskCreate, TasksService } from "@/client"
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
import useCustomToast from "@/hooks/useCustomToast"
import { queryKeys } from "@/lib/queryKeys"
import { handleError } from "@/utils"

const formSchema = z.object({
  start_time: z.string().min(1),
  finish_time: z.string().min(1),
  comment: z.string().min(1),
  employee_id: z.coerce.number().int().positive(),
  task_type_id: z.coerce.number().int().positive(),
  agent_point_id: z.coerce.number().int().positive(),
  task_status_id: z.coerce.number().int().positive(),
})

type FormData = z.infer<typeof formSchema>

const toIsoDateTime = (value: string) => new Date(value).toISOString()

const AddUser = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
  })

  const mutation = useMutation({
    mutationFn: (data: TaskCreate) =>
      TasksService.createTask({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Task created successfully")
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
      start_time: toIsoDateTime(data.start_time),
      finish_time: toIsoDateTime(data.finish_time),
    })
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className="my-4">
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
                      <Input placeholder="Описание задачи" type="text" {...field} />
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
                    <FormLabel>ID сотрудника</FormLabel>
                    <FormControl>
                      <Input placeholder="1" type="number" {...field} />
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
                    <FormLabel>ID типа задачи</FormLabel>
                    <FormControl>
                      <Input placeholder="1" type="number" {...field} />
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
                    <FormLabel>ID агентской точки</FormLabel>
                    <FormControl>
                      <Input placeholder="1" type="number" {...field} />
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
                    <FormLabel>ID статуса задачи</FormLabel>
                    <FormControl>
                      <Input placeholder="1" type="number" {...field} />
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
