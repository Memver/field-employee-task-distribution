import { zodResolver } from "@hookform/resolvers/zod"
import { Pencil } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
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
import { useTaskCarryoverFormOptions } from "@/features/taskCarryovers/formOptions"
import { useUpdateTaskCarryoverMutation } from "@/features/taskCarryovers/mutations"
import type {
  TaskCarryoverPublic,
  TaskCarryoverUpdate,
} from "@/features/taskCarryovers/types"

const formSchema = z.object({
  agent_point_id: z
    .number()
    .int()
    .positive({ message: "Выберите агентскую точку" }),
  task_type_id: z.number().int().positive({ message: "Выберите тип задачи" }),
  planned_for_date: z.string().min(1, { message: "Дата обязательна" }),
  carryover_days: z
    .number({ invalid_type_error: "Укажите число дней" })
    .int()
    .positive({ message: "Должно быть больше 0" }),
  source_reason: z.string().min(1, { message: "Укажите причину" }),
})

type FormData = z.infer<typeof formSchema>

type Props = {
  taskCarryover: TaskCarryoverPublic
  onSuccess: () => void
}

function EditTaskCarryover({ taskCarryover, onSuccess }: Props) {
  const [isOpen, setIsOpen] = useState(false)
  const options = useTaskCarryoverFormOptions()
  const mutation = useUpdateTaskCarryoverMutation(() => {
    setIsOpen(false)
    onSuccess()
  })

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      agent_point_id: taskCarryover.agent_point_id,
      task_type_id: taskCarryover.task_type_id,
      planned_for_date: taskCarryover.planned_for_date,
      carryover_days: taskCarryover.carryover_days,
      source_reason: taskCarryover.source_reason,
    },
    mode: "onBlur",
    criteriaMode: "all",
  })

  const onSubmit = (data: FormData) => {
    const payload: TaskCarryoverUpdate = {
      ...data,
      source_reason: data.source_reason.trim(),
    }
    mutation.mutate({
      taskCarryoverId: taskCarryover.id,
      requestBody: payload,
    })
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem
        onSelect={(event) => event.preventDefault()}
        onClick={() => setIsOpen(true)}
      >
        <Pencil />
        Редактировать перенос
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Редактировать перенос</DialogTitle>
          <DialogDescription>
            Обновите данные перенесенной задачи.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="agent_point_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Агентская точка</FormLabel>
                    <FormControl>
                      <RelationSelect
                        value={field.value ? String(field.value) : ""}
                        onChange={(value) => field.onChange(Number(value))}
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
                name="task_type_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Тип задачи</FormLabel>
                    <FormControl>
                      <RelationSelect
                        value={field.value ? String(field.value) : ""}
                        onChange={(value) => field.onChange(Number(value))}
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
                name="planned_for_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Дата переноса</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="carryover_days"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Дней переноса</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min={1}
                        value={field.value ?? 1}
                        onChange={(event) =>
                          field.onChange(Number(event.target.value))
                        }
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="source_reason"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Причина</FormLabel>
                    <FormControl>
                      <Input placeholder="Причина переноса" {...field} />
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

export default EditTaskCarryover
