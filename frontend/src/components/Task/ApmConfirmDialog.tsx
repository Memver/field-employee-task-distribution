import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type TaskPublic, TasksService } from "@/client"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import useCustomToast from "@/hooks/useCustomToast"
import { apmVerdictOptions, toasts } from "@/lib/i18n/ru"
import { queryKeys } from "@/lib/queryKeys"
import { handleError } from "@/utils"

type VerdictValue = "pending" | "confirmed" | "rejected"

const formSchema = z.object({
  verdict: z.enum(["pending", "confirmed", "rejected"]),
  comment: z.string().optional(),
})

type FormData = z.infer<typeof formSchema>

function verdictFromTask(task: TaskPublic): VerdictValue {
  if (task.ap_manager_confirmed == null) {
    return "pending"
  }
  return task.ap_manager_confirmed ? "confirmed" : "rejected"
}

function confirmedFromVerdict(verdict: VerdictValue): boolean | null {
  if (verdict === "pending") {
    return null
  }
  return verdict === "confirmed"
}

interface ApmConfirmDialogProps {
  task: TaskPublic
}

export function ApmConfirmDialog({ task }: ApmConfirmDialogProps) {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      verdict: verdictFromTask(task),
      comment: task.ap_manager_comment ?? "",
    },
  })

  useEffect(() => {
    if (isOpen) {
      form.reset({
        verdict: verdictFromTask(task),
        comment: task.ap_manager_comment ?? "",
      })
    }
  }, [isOpen, task, form])

  const mutation = useMutation({
    mutationFn: (data: FormData) =>
      TasksService.completeTaskByAgentPointManager({
        taskId: task.id,
        requestBody: {
          confirmed: confirmedFromVerdict(data.verdict),
          comment: data.comment?.trim() || null,
        },
      }),
    onSuccess: () => {
      showSuccessToast(toasts.taskVerdictSaved)
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.admin })
    },
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          Вердикт
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Вердикт по задаче</DialogTitle>
          <DialogDescription>
            Выберите вердикт по выполнению задачи на вашей агентской точке.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form
            className="space-y-4"
            onSubmit={form.handleSubmit((data) => mutation.mutate(data))}
          >
            <FormField
              control={form.control}
              name="verdict"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Вердикт</FormLabel>
                  <Select value={field.value} onValueChange={field.onChange}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Выберите вердикт" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {apmVerdictOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
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
                    <Input placeholder="Комментарий (необязательно)" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <DialogFooter className="gap-2 sm:gap-0">
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
